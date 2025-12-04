#!/usr/bin/env bash
set -euo pipefail

# Handle --reset flag
RESET=false
if [[ "${1:-}" == "--reset" ]]; then
  RESET=true
fi

if [ ! -f .env ]; then
  echo ".env file not found. Create a .env file with SUBSCRIPTION_ID."
  exit 1
fi

source .env
: "${SUBSCRIPTION_ID:?SUBSCRIPTION_ID is not set in .env}"

LOCATION="brazilsouth"
RESOURCE_GROUP="ai-engineering"

# Reset logic: Delete everything if requested
if [ "$RESET" = true ]; then
  echo "WARNING: You are about to delete the Resource Group '$RESOURCE_GROUP' and all its resources."
  echo "This includes Storage Accounts, Synapse Workspaces, SQL Pools, Service Principal, and data."
  
  # Delete Service Principal (lives in Azure AD, not Resource Group)
  SP_NAME="srag-poc"
  EXISTING_SP=$(az ad sp list --display-name "$SP_NAME" --query "[0].id" -o tsv 2>/dev/null || echo "")
  if [ -n "$EXISTING_SP" ]; then
    echo "Deleting Service Principal: $SP_NAME"
    az ad sp delete --id "$EXISTING_SP" 2>/dev/null || echo "Warning: Could not delete Service Principal"
  fi
  
  # Delete Resource Group (cascades to all contained resources)
  EXISTING_RG=$(az group show --name "$RESOURCE_GROUP" --query "name" -o tsv 2>/dev/null || echo "")
  if [ -n "$EXISTING_RG" ]; then
    echo "Deleting Resource Group (runs in background)..."
    az group delete --name "$RESOURCE_GROUP" --yes --no-wait
    echo "Resource Group deletion initiated. Check Azure Portal for status."
  else
    echo "Resource Group '$RESOURCE_GROUP' does not exist."
  fi
  
  echo "Reset complete."
  exit 0
fi

STORAGE_ACCOUNT_NAME="desafioai"
FILE_SYSTEM_NAME="desafio-ai"
DIRECTORIES=("raw" "processed" "outputs")
SYNAPSE_WORKSPACE_NAME="${AZURE_SYNAPSE_WORKSPACE_NAME:-desafio-synapse}"
SQL_POOL_NAME="${AZURE_SQL_POOL_NAME:-desafiodw}"
# Use DW100c for Free Trial compatibility (lowest cost)
SQL_POOL_PERFORMANCE_LEVEL="${AZURE_SQL_POOL_PERFORMANCE_LEVEL:-DW100c}"

az account set --subscription "$SUBSCRIPTION_ID"

# Check if Resource Group exists
EXISTING_RG=$(az group show --name "$RESOURCE_GROUP" --query "name" -o tsv 2>/dev/null || echo "")
if [ -z "$EXISTING_RG" ]; then
  echo "Creating Resource Group: $RESOURCE_GROUP"
  az group create --name "$RESOURCE_GROUP" --location "$LOCATION" >/dev/null
else
  echo "Resource Group '$RESOURCE_GROUP' already exists, skipping creation."
fi

# Check if Storage Account exists
EXISTING_SA=$(az storage account list \
  --resource-group "$RESOURCE_GROUP" \
  --query "[?name=='$STORAGE_ACCOUNT_NAME'].name" \
  -o tsv 2>/dev/null || echo "")

if [ -z "$EXISTING_SA" ]; then
  echo "Creating Storage Account: $STORAGE_ACCOUNT_NAME"
  az storage account create \
    --name "$STORAGE_ACCOUNT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --sku Standard_LRS \
    --kind StorageV2 \
    --enable-hierarchical-namespace true \
    --min-tls-version TLS1_2 \
    --allow-blob-public-access false \
    >/dev/null
else
  echo "Storage Account '$STORAGE_ACCOUNT_NAME' already exists, skipping creation."
fi

# Check if File System exists
EXISTING_FS=$(az storage fs show \
  --name "$FILE_SYSTEM_NAME" \
  --account-name "$STORAGE_ACCOUNT_NAME" \
  --auth-mode login \
  --query "name" \
  -o tsv 2>/dev/null || echo "")

if [ -z "$EXISTING_FS" ]; then
  echo "Creating File System: $FILE_SYSTEM_NAME"
  FS_OUTPUT=$(timeout 10 az storage fs create \
    --name "$FILE_SYSTEM_NAME" \
    --account-name "$STORAGE_ACCOUNT_NAME" \
    --auth-mode login \
    2>&1) || true
else
  echo "File System '$FILE_SYSTEM_NAME' already exists, skipping creation."
fi

# Create directories if they don't exist
echo "Checking Data Lake directories..."
for dir in "${DIRECTORIES[@]}"; do
  EXISTING_DIR=$(az storage fs directory show \
    --file-system "$FILE_SYSTEM_NAME" \
    --name "$dir" \
    --account-name "$STORAGE_ACCOUNT_NAME" \
    --auth-mode login \
    --query "name" \
    -o tsv 2>/dev/null || echo "")
  
  if [ -z "$EXISTING_DIR" ]; then
    echo "Creating directory: $dir"
    timeout 10 az storage fs directory create \
      --file-system "$FILE_SYSTEM_NAME" \
      --name "$dir" \
      --account-name "$STORAGE_ACCOUNT_NAME" \
      --auth-mode login \
      >/dev/null 2>&1 || true
  else
    echo "Directory '$dir' already exists, skipping."
  fi
done

SP_NAME="srag-poc"
STORAGE_ACCOUNT_ID="/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.Storage/storageAccounts/${STORAGE_ACCOUNT_NAME}"

# Try to load existing credentials from .secrets file or .env
SECRETS_FILE=".secrets/azure-credentials.txt"
EXISTING_CLIENT_ID="${AZURE_CLIENT_ID:-}"
EXISTING_CLIENT_SECRET="${AZURE_CLIENT_SECRET:-}"

if [ -z "$EXISTING_CLIENT_SECRET" ] && [ -f "$SECRETS_FILE" ]; then
  EXISTING_CLIENT_SECRET=$(grep "^AZURE_CLIENT_SECRET=" "$SECRETS_FILE" 2>/dev/null | cut -d'=' -f2- || echo "")
  if [ -z "$EXISTING_CLIENT_ID" ]; then
    EXISTING_CLIENT_ID=$(grep "^AZURE_CLIENT_ID=" "$SECRETS_FILE" 2>/dev/null | cut -d'=' -f2- || echo "")
  fi
fi

# Check if Service Principal already exists
EXISTING_SP=$(az ad sp list \
  --display-name "$SP_NAME" \
  --query "[0].appId" \
  -o tsv 2>/dev/null || echo "")

if [ -n "$EXISTING_SP" ]; then
  echo "Service Principal '$SP_NAME' already exists."
  
  # Check and assign role if needed
  ROLE_ASSIGNMENT=$(az role assignment list \
    --scope "$STORAGE_ACCOUNT_ID" \
    --assignee "$EXISTING_SP" \
    --role "Storage Blob Data Contributor" \
    --query "[0].id" \
    -o tsv 2>/dev/null || echo "")
  
  if [ -z "$ROLE_ASSIGNMENT" ]; then
    echo "Assigning role to existing Service Principal..."
    az role assignment create \
      --role "Storage Blob Data Contributor" \
      --assignee "$EXISTING_SP" \
      --scope "$STORAGE_ACCOUNT_ID" \
      >/dev/null
  else
    echo "Role assignment already exists, skipping."
  fi
  
  # Use existing credentials if available, otherwise reset
  if [ -n "$EXISTING_CLIENT_SECRET" ] && [ "$EXISTING_CLIENT_SECRET" != "<MANUAL_SETUP_REQUIRED>" ] && [ "$EXISTING_CLIENT_SECRET" != "<CHECK_AZURE_PORTAL_FOR_SECRET>" ]; then
    echo "Using existing Service Principal credentials from secrets."
    CLIENT_ID="$EXISTING_SP"
    CLIENT_SECRET="$EXISTING_CLIENT_SECRET"
    TENANT_ID=$(az account show --query tenantId -o tsv)
  else
    echo "No existing secret found. Resetting Service Principal credentials..."
    SP_OUTPUT=$(az ad sp credential reset \
      --id "$EXISTING_SP" \
      --output json 2>/dev/null || echo "")
    
    if [ -n "$SP_OUTPUT" ]; then
      CLIENT_ID="$EXISTING_SP"
      CLIENT_SECRET=$(echo "$SP_OUTPUT" | python3 -c "import sys, json; print(json.load(sys.stdin)['password'])" 2>/dev/null || echo "")
      TENANT_ID=$(az account show --query tenantId -o tsv)
    else
      CLIENT_ID="$EXISTING_SP"
      CLIENT_SECRET="<MANUAL_SETUP_REQUIRED>"
      TENANT_ID=$(az account show --query tenantId -o tsv)
    fi
  fi
else
  echo "Creating Service Principal: $SP_NAME"
  SP_OUTPUT=$(az ad sp create-for-rbac \
    --name "$SP_NAME" \
    --role "Storage Blob Data Contributor" \
    --scopes "$STORAGE_ACCOUNT_ID" \
    --output json 2>/dev/null)
  
  if [ -z "$SP_OUTPUT" ]; then
    echo "ERROR: Error creating Service Principal. Please check your Azure CLI permissions."
    exit 1
  fi
  
  CLIENT_ID=$(echo "$SP_OUTPUT" | python3 -c "import sys, json; print(json.load(sys.stdin)['appId'])" 2>/dev/null || echo "")
  CLIENT_SECRET=$(echo "$SP_OUTPUT" | python3 -c "import sys, json; print(json.load(sys.stdin)['password'])" 2>/dev/null || echo "")
  TENANT_ID=$(echo "$SP_OUTPUT" | python3 -c "import sys, json; print(json.load(sys.stdin)['tenant'])" 2>/dev/null || echo "")
  
  if [ -z "$CLIENT_ID" ] || [ -z "$CLIENT_SECRET" ]; then
    CLIENT_ID=$(az ad sp list --display-name "$SP_NAME" --query "[0].appId" -o tsv)
    TENANT_ID=$(az account show --query tenantId -o tsv)
    CLIENT_SECRET="<CHECK_AZURE_PORTAL_FOR_SECRET>"
  fi
fi

# Azure Synapse Analytics Configuration

# Check if Synapse Workspace already exists first (needed for credential handling)
EXISTING_WORKSPACE=$(az synapse workspace show \
  --name "$SYNAPSE_WORKSPACE_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "name" \
  -o tsv 2>/dev/null || echo "")

# Try to load SQL Admin credentials from multiple sources
# Priority: 1) Environment vars, 2) Secrets file, 3) Generate new (only if workspace doesn't exist)
if [ -z "${AZURE_SQL_ADMIN_USER:-}" ]; then
  # Try to load from secrets file
  if [ -f "$SECRETS_FILE" ]; then
    AZURE_SQL_ADMIN_USER=$(grep "^AZURE_SQL_ADMIN_USER=" "$SECRETS_FILE" 2>/dev/null | cut -d'=' -f2- || echo "")
  fi
  
  # If still empty and workspace exists, try to get from workspace
  if [ -z "$AZURE_SQL_ADMIN_USER" ] && [ -n "$EXISTING_WORKSPACE" ]; then
    AZURE_SQL_ADMIN_USER=$(az synapse workspace show \
      --name "$SYNAPSE_WORKSPACE_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --query "sqlAdministratorLogin" \
      -o tsv 2>/dev/null || echo "")
    if [ -n "$AZURE_SQL_ADMIN_USER" ]; then
      echo "Recovered SQL Admin username from existing workspace: $AZURE_SQL_ADMIN_USER"
    fi
  fi
  
  # Generate new only if workspace doesn't exist
  if [ -z "$AZURE_SQL_ADMIN_USER" ] && [ -z "$EXISTING_WORKSPACE" ]; then
    AZURE_SQL_ADMIN_USER="sqladmin${RANDOM}"
  fi
fi

if [ -z "${AZURE_SQL_ADMIN_PASSWORD:-}" ]; then
  # Try to load from secrets file
  if [ -f "$SECRETS_FILE" ]; then
    AZURE_SQL_ADMIN_PASSWORD=$(grep "^AZURE_SQL_ADMIN_PASSWORD=" "$SECRETS_FILE" 2>/dev/null | cut -d'=' -f2- || echo "")
    if [ -n "$AZURE_SQL_ADMIN_PASSWORD" ]; then
      echo "Using existing SQL Admin password from secrets file."
    fi
  fi
  
  # Generate new only if workspace doesn't exist
  if [ -z "$AZURE_SQL_ADMIN_PASSWORD" ] && [ -z "$EXISTING_WORKSPACE" ]; then
    # Generate a secure password that meets Azure SQL requirements:
    # - At least 8 characters
    # - Contains uppercase, lowercase, numbers, and special characters
    BASE_PASS=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-12)
    AZURE_SQL_ADMIN_PASSWORD="${BASE_PASS}Aa1!"
  elif [ -z "$AZURE_SQL_ADMIN_PASSWORD" ] && [ -n "$EXISTING_WORKSPACE" ]; then
    echo "WARNING: Synapse Workspace exists but SQL Admin password not found in secrets."
    echo "Password cannot be recovered from Azure. Please check your .secrets/azure-credentials.txt file."
    AZURE_SQL_ADMIN_PASSWORD="<PASSWORD_NOT_RECOVERABLE>"
  fi
fi

if [ -n "$AZURE_SQL_ADMIN_USER" ]; then
  if [ -n "$EXISTING_WORKSPACE" ]; then
    echo "Synapse Workspace '$SYNAPSE_WORKSPACE_NAME' already exists, skipping creation."
  else
    echo "Creating Synapse Workspace: $SYNAPSE_WORKSPACE_NAME"
    WORKSPACE_OUTPUT=$(az synapse workspace create \
      --name "$SYNAPSE_WORKSPACE_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --storage-account "$STORAGE_ACCOUNT_NAME" \
      --file-system "$FILE_SYSTEM_NAME" \
      --sql-admin-login-user "$AZURE_SQL_ADMIN_USER" \
      --sql-admin-login-password "$AZURE_SQL_ADMIN_PASSWORD" \
      --location "$LOCATION" \
      --output json 2>&1)
    
    if [ $? -eq 0 ]; then
      echo "Synapse Workspace created successfully."
      echo "Waiting for workspace to be fully ready..."
      sleep 10
    else
      echo "Warning: Synapse Workspace creation may have failed."
      echo "$WORKSPACE_OUTPUT" | grep -i "error\|failed" || true
    fi
  fi

  # Check if SQL Pool (Data Warehouse) exists
  EXISTING_SQL_POOL=$(az synapse sql pool show \
    --name "$SQL_POOL_NAME" \
    --workspace-name "$SYNAPSE_WORKSPACE_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "name" \
    -o tsv 2>/dev/null || echo "")

  if [ -n "$EXISTING_SQL_POOL" ]; then
    echo "SQL Pool '$SQL_POOL_NAME' already exists, skipping creation."
    # Recover performance level from existing pool
    EXISTING_PERF_LEVEL=$(az synapse sql pool show \
      --name "$SQL_POOL_NAME" \
      --workspace-name "$SYNAPSE_WORKSPACE_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --query "sku.name" \
      -o tsv 2>/dev/null || echo "")
    if [ -n "$EXISTING_PERF_LEVEL" ]; then
      SQL_POOL_PERFORMANCE_LEVEL="$EXISTING_PERF_LEVEL"
      echo "Recovered performance level from existing pool: $SQL_POOL_PERFORMANCE_LEVEL"
    fi
  else
    echo "Creating SQL Pool (Data Warehouse): $SQL_POOL_NAME"
    echo "Performance Level: $SQL_POOL_PERFORMANCE_LEVEL"
    
    set +e
    SQL_POOL_OUTPUT=$(az synapse sql pool create \
      --name "$SQL_POOL_NAME" \
      --workspace-name "$SYNAPSE_WORKSPACE_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --performance-level "$SQL_POOL_PERFORMANCE_LEVEL" \
      --collation "SQL_Latin1_General_CP1_CI_AS" \
      --no-wait \
      --output json 2>&1)
    SQL_POOL_EXIT_CODE=$?
    set -e
    
    if [ $SQL_POOL_EXIT_CODE -eq 0 ]; then
      echo "SQL Pool creation initiated (running in background)."
      echo "Waiting for pool to be ready..."
      sleep 15
    else
      echo "Warning: SQL Pool creation failed. Continuing with setup..."
      echo "Error details:"
      echo "$SQL_POOL_OUTPUT"
      echo ""
      echo "Note: SQL Pool creation may fail on Free Trial due to quota limits."
      echo "You can create it manually via Azure Portal or try again later."
    fi
  fi

  # Get Synapse Workspace details for connection string
  SYNAPSE_SQL_ENDPOINT=$(az synapse workspace show \
    --name "$SYNAPSE_WORKSPACE_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "connectivityEndpoints.sql" \
    -o tsv 2>/dev/null || echo "")

  # Grant Synapse Managed Identity access to Storage Account for COPY INTO
  echo "Configuring Synapse Managed Identity access to Storage..."
  SYNAPSE_IDENTITY=$(az synapse workspace show \
    --name "$SYNAPSE_WORKSPACE_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "identity.principalId" \
    -o tsv 2>/dev/null || echo "")
  
  if [ -n "$SYNAPSE_IDENTITY" ]; then
    # Check if role already assigned
    SYNAPSE_ROLE=$(az role assignment list \
      --scope "$STORAGE_ACCOUNT_ID" \
      --assignee "$SYNAPSE_IDENTITY" \
      --role "Storage Blob Data Contributor" \
      --query "[0].id" \
      -o tsv 2>/dev/null || echo "")
    
    if [ -z "$SYNAPSE_ROLE" ]; then
      echo "Assigning Storage Blob Data Contributor to Synapse Managed Identity..."
      az role assignment create \
        --role "Storage Blob Data Contributor" \
        --assignee "$SYNAPSE_IDENTITY" \
        --scope "$STORAGE_ACCOUNT_ID" \
        >/dev/null 2>&1 || echo "Warning: Could not assign role (may already exist)"
    else
      echo "Synapse Managed Identity already has Storage Blob Data Contributor role."
    fi
  fi

  # Try to load existing Storage Key and SAS Token from secrets
  STORAGE_KEY="${AZURE_STORAGE_KEY:-}"
  SAS_TOKEN="${AZURE_STORAGE_SAS_TOKEN:-}"
  
  if [ -z "$STORAGE_KEY" ] && [ -f "$SECRETS_FILE" ]; then
    STORAGE_KEY=$(grep "^AZURE_STORAGE_KEY=" "$SECRETS_FILE" 2>/dev/null | cut -d'=' -f2- || echo "")
  fi
  if [ -z "$SAS_TOKEN" ] && [ -f "$SECRETS_FILE" ]; then
    SAS_TOKEN=$(grep "^AZURE_STORAGE_SAS_TOKEN=" "$SECRETS_FILE" 2>/dev/null | cut -d'=' -f2- || echo "")
  fi
  
  # Get Storage Key if not already available
  if [ -z "$STORAGE_KEY" ]; then
    echo "Retrieving Storage Account key..."
    STORAGE_KEY=$(az storage account keys list \
      --account-name "$STORAGE_ACCOUNT_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --query "[0].value" \
      -o tsv 2>/dev/null || echo "")
  else
    echo "Using existing Storage Account key from secrets."
  fi
  
  # Generate SAS token only if not already available or if empty
  if [ -z "$SAS_TOKEN" ]; then
    echo "Generating SAS token for bulk data operations..."
    SAS_EXPIRY=$(date -u -v+1y '+%Y-%m-%dT%H:%MZ' 2>/dev/null || date -u -d '+1 year' '+%Y-%m-%dT%H:%MZ' 2>/dev/null || echo "2026-01-01T00:00Z")
    
    if [ -n "$STORAGE_KEY" ]; then
      SAS_TOKEN=$(az storage container generate-sas \
        --account-name "$STORAGE_ACCOUNT_NAME" \
        --account-key "$STORAGE_KEY" \
        --name "$FILE_SYSTEM_NAME" \
        --permissions racwdl \
        --expiry "$SAS_EXPIRY" \
        --output tsv 2>/dev/null || echo "")
      
      if [ -n "$SAS_TOKEN" ]; then
        echo "SAS token generated successfully (expires: $SAS_EXPIRY)"
      else
        echo "Warning: Could not generate SAS token. COPY INTO may not work."
      fi
    fi
  else
    echo "Using existing SAS token from secrets."
  fi

  # Configure firewall rule with current client IP
  CURRENT_IP=$(curl -s https://api.ipify.org 2>/dev/null || echo "")
  if [ -n "$CURRENT_IP" ]; then
    echo "Checking firewall rules for IP: $CURRENT_IP"
    
    # Check if IP is already allowed in any existing firewall rule
    IP_ALLOWED=false
    FIREWALL_RULES=$(az synapse workspace firewall-rule list \
      --resource-group "$RESOURCE_GROUP" \
      --workspace-name "$SYNAPSE_WORKSPACE_NAME" \
      --query "[].{startIp:startIpAddress, endIp:endIpAddress}" \
      -o tsv 2>/dev/null || echo "")
    
    if [ -n "$FIREWALL_RULES" ]; then
      while IFS=$'\t' read -r START_IP END_IP; do
        if [ -n "$START_IP" ] && [ -n "$END_IP" ]; then
          # Check if rule allows all IPs (0.0.0.0) or matches current IP exactly
          if [ "$START_IP" = "0.0.0.0" ] || ([ "$START_IP" = "$CURRENT_IP" ] && [ "$END_IP" = "$CURRENT_IP" ]); then
            IP_ALLOWED=true
            echo "IP $CURRENT_IP is already allowed by firewall rule ($START_IP - $END_IP)"
            break
          fi
        fi
      done <<< "$FIREWALL_RULES"
    fi
    
    if [ "$IP_ALLOWED" = false ]; then
      RULE_NAME="ClientIP_${CURRENT_IP//./_}"
      echo "IP $CURRENT_IP not found in firewall rules. Adding firewall rule..."
      FIREWALL_OUTPUT=$(az synapse workspace firewall-rule create \
        --resource-group "$RESOURCE_GROUP" \
        --workspace-name "$SYNAPSE_WORKSPACE_NAME" \
        --name "$RULE_NAME" \
        --start-ip-address "$CURRENT_IP" \
        --end-ip-address "$CURRENT_IP" \
        --output json 2>&1)
      
      if [ $? -eq 0 ]; then
        echo "Firewall rule added successfully for IP $CURRENT_IP"
      else
        echo "Warning: Firewall rule creation may have failed."
        echo "$FIREWALL_OUTPUT" | grep -i "error\|failed" || true
        echo "You may need to add your IP manually via Azure Portal."
      fi
    fi
  else
    echo "Warning: Could not detect current IP address. Firewall rule not created."
    echo "You may need to add your IP manually via Azure Portal."
  fi
fi

echo
echo "AZURE CREDENTIALS"
echo "=================="
echo "Add these to your .env file:"
echo
echo "AZURE_CLIENT_ID=${CLIENT_ID}"
echo "AZURE_CLIENT_SECRET=${CLIENT_SECRET}"
echo "AZURE_TENANT_ID=${TENANT_ID}"
echo "STORAGE_ACCOUNT_NAME=${STORAGE_ACCOUNT_NAME}"
echo "AZURE_SYNAPSE_WORKSPACE_NAME=${SYNAPSE_WORKSPACE_NAME}"
echo "AZURE_SQL_POOL_NAME=${SQL_POOL_NAME}"
if [ -n "$SYNAPSE_SQL_ENDPOINT" ]; then
  echo "AZURE_SYNAPSE_SQL_ENDPOINT=${SYNAPSE_SQL_ENDPOINT}"
fi
echo "AZURE_SQL_ADMIN_USER=${AZURE_SQL_ADMIN_USER}"
echo "AZURE_SQL_ADMIN_PASSWORD=${AZURE_SQL_ADMIN_PASSWORD}"
echo "AZURE_SQL_POOL_PERFORMANCE_LEVEL=${SQL_POOL_PERFORMANCE_LEVEL}"
if [ -n "${STORAGE_KEY:-}" ]; then
  echo "AZURE_STORAGE_KEY=${STORAGE_KEY}"
fi
if [ -n "${SAS_TOKEN:-}" ]; then
  echo "AZURE_STORAGE_SAS_TOKEN=${SAS_TOKEN}"
fi
echo

# Save credentials to .secrets/ directory (not tracked by git)
SECRETS_DIR=".secrets"
mkdir -p "$SECRETS_DIR"
SECRETS_FILE="${SECRETS_DIR}/azure-credentials.txt"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

{
  echo "# Azure Credentials"
  echo "# Generated on: ${TIMESTAMP}"
  echo "# WARNING: This file contains sensitive information. Do not commit to git."
  echo
  echo "AZURE_CLIENT_ID=${CLIENT_ID}"
  echo "AZURE_CLIENT_SECRET=${CLIENT_SECRET}"
  echo "AZURE_TENANT_ID=${TENANT_ID}"
  echo "STORAGE_ACCOUNT_NAME=${STORAGE_ACCOUNT_NAME}"
  echo "AZURE_SYNAPSE_WORKSPACE_NAME=${SYNAPSE_WORKSPACE_NAME}"
  echo "AZURE_SQL_POOL_NAME=${SQL_POOL_NAME}"
} > "$SECRETS_FILE"

if [ -n "${SYNAPSE_SQL_ENDPOINT:-}" ]; then
  echo "AZURE_SYNAPSE_SQL_ENDPOINT=${SYNAPSE_SQL_ENDPOINT}" >> "$SECRETS_FILE"
fi

{
  echo "AZURE_SQL_ADMIN_USER=${AZURE_SQL_ADMIN_USER}"
  echo "AZURE_SQL_ADMIN_PASSWORD=${AZURE_SQL_ADMIN_PASSWORD}"
  echo "AZURE_SQL_POOL_PERFORMANCE_LEVEL=${SQL_POOL_PERFORMANCE_LEVEL}"
} >> "$SECRETS_FILE"

if [ -n "${STORAGE_KEY:-}" ]; then
  echo "AZURE_STORAGE_KEY=${STORAGE_KEY}" >> "$SECRETS_FILE"
fi
if [ -n "${SAS_TOKEN:-}" ]; then
  echo "AZURE_STORAGE_SAS_TOKEN=${SAS_TOKEN}" >> "$SECRETS_FILE"
fi

echo "Credentials saved to: ${SECRETS_FILE}"
echo
