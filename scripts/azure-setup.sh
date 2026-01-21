#!/usr/bin/env bash
set -euo pipefail

# --- 1. Header and globals ---
# Handle --reset and --storage-only flags
RESET=false
STORAGE_ONLY=false
if [[ "${1:-}" == "--reset" ]]; then
  RESET=true
fi
if [[ "${1:-}" == "--storage-only" ]]; then
  STORAGE_ONLY=true
fi

log_info() { echo "[INFO] $*"; }
log_ok()   { echo "[OK]   $*"; }
log_skip() { echo "[SKIP] $*"; }
log_warn() { echo "[WARN] $*"; }
log_err()  { echo "[ERR]  $*"; }

# Load environment variables if present (do not hard-fail if missing)
if [ -f .env ]; then
  set -a
  source .env
  set +a
  if [ -z "${SUBSCRIPTION_ID:-}" ]; then
    log_err "SUBSCRIPTION_ID is required in .env when .env exists. Add SUBSCRIPTION_ID (from Azure Portal or 'az account show --query id -o tsv') to .env and rerun."
    exit 1
  fi
fi

# --- 2. Azure CLI and subscription ---
# Ensure Azure CLI is logged in; fallback to az login if needed
ACCOUNT_SHOW=$(az account show --output json 2>/dev/null || true)
if [ -z "$ACCOUNT_SHOW" ]; then
  log_info "Not logged in to Azure CLI. Starting interactive login..."
  az login >/dev/null
  ACCOUNT_SHOW=$(az account show --output json 2>/dev/null || true)
  if [ -z "$ACCOUNT_SHOW" ]; then
    log_err "Unable to log in to Azure CLI. Please run 'az login' and retry."
    exit 1
  fi
fi

# Determine subscription and tenant
DEFAULT_SUBSCRIPTION_ID=$(echo "$ACCOUNT_SHOW" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data.get('id',''))" 2>/dev/null || echo "")
DEFAULT_TENANT_ID=$(echo "$ACCOUNT_SHOW" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data.get('tenantId',''))" 2>/dev/null || echo "")

SUBSCRIPTION_ID="${SUBSCRIPTION_ID:-$DEFAULT_SUBSCRIPTION_ID}"

if [ -z "$SUBSCRIPTION_ID" ]; then
  log_err "No subscription found in Azure CLI and none provided in .env."
  log_err "Please create/assign a subscription in the Azure Portal and rerun."
  exit 1
fi

# Validate the subscription exists for the current login
SUBSCRIPTION_ROW=$(az account list --query "[?id=='$SUBSCRIPTION_ID'].[id,tenantId]" -o tsv 2>/dev/null || true)
if [ -z "$SUBSCRIPTION_ROW" ]; then
  log_err "Subscription '$SUBSCRIPTION_ID' not available for the current login."
  log_err "Run 'az login' with the correct account/tenant or update SUBSCRIPTION_ID in .env."
  exit 1
fi

TENANT_ID=$(echo "$SUBSCRIPTION_ROW" | awk '{print $2}')
TENANT_ID="${TENANT_ID:-$DEFAULT_TENANT_ID}"

log_info "Using subscription: $SUBSCRIPTION_ID (tenant: ${TENANT_ID:-unknown})"
az account set --subscription "$SUBSCRIPTION_ID"

# Register required resource providers (skip Synapse/Sql when --storage-only or --reset)
log_info "Ensuring required resource providers are registered..."
if [ "$RESET" = true ] || [ "$STORAGE_ONLY" = true ]; then
  REQUIRED_PROVIDERS=("Microsoft.Storage")
else
  REQUIRED_PROVIDERS=("Microsoft.Storage" "Microsoft.Synapse" "Microsoft.Sql")
fi
for provider in "${REQUIRED_PROVIDERS[@]}"; do
  STATE=$(az provider show --namespace "$provider" --query "registrationState" -o tsv 2>/dev/null || echo "NotRegistered")
  if [ "$STATE" != "Registered" ]; then
    log_info "Registering provider: $provider"
    az provider register --namespace "$provider" --wait >/dev/null 2>&1 || log_warn "Could not register $provider (may already be in progress)"
  fi
done

LOCATION="brazilsouth"
RESOURCE_GROUP="ai-engineering"

# --- 3. Reset path ---
# --reset: delete everything created by the script. Check-if-exists then delete for each.
if [ "$RESET" = true ]; then
  log_warn "You are about to delete everything created by this script: Service Principal, App Registration, and Resource Group (Storage, Synapse, SQL Pool, firewall, etc.)."
  
  SP_NAME="srag-poc"
  
  # Service Principal and App Registration (created by create-for-rbac; live in Azure AD)
  EXISTING_SP=$(az ad sp list --display-name "$SP_NAME" --query "[0].id" -o tsv 2>/dev/null || echo "")
  EXISTING_APP_ID=$(az ad sp list --display-name "$SP_NAME" --query "[0].appId" -o tsv 2>/dev/null || echo "")
  if [ -n "$EXISTING_SP" ]; then
    log_info "Deleting Service Principal: $SP_NAME"
    az ad sp delete --id "$EXISTING_SP" 2>/dev/null || log_warn "Could not delete Service Principal"
    if [ -n "$EXISTING_APP_ID" ]; then
      log_info "Deleting App Registration: $EXISTING_APP_ID"
      az ad app delete --id "$EXISTING_APP_ID" 2>/dev/null || log_warn "Could not delete App Registration (may already be removed)"
    fi
  else
    log_skip "Service Principal '$SP_NAME' does not exist"
  fi
  
  # Resource Group (cascades to: Storage Account, File System, directories, Synapse Workspace, SQL Pool, firewall rules, role assignments on those resources)
  EXISTING_RG=$(az group show --name "$RESOURCE_GROUP" --query "name" -o tsv 2>/dev/null || echo "")
  if [ -n "$EXISTING_RG" ]; then
    log_info "Deleting Resource Group: $RESOURCE_GROUP (runs in background; cascades to Storage, Synapse, SQL Pool, etc.)"
    az group delete --name "$RESOURCE_GROUP" --yes --no-wait
    log_info "Resource Group deletion initiated. Check Azure Portal for status."
  else
    log_skip "Resource Group '$RESOURCE_GROUP' does not exist"
  fi
  
  log_ok "Reset complete."
  exit 0
fi

STORAGE_ACCOUNT_BASE="desafioai"
STORAGE_ACCOUNT_NAME="${AZURE_STORAGE_ACCOUNT_NAME:-}"
FILE_SYSTEM_NAME="desafio-ai"
DIRECTORIES=("raw" "processed" "outputs" "clean")

# Generate unique suffix from subscription ID (portable: md5sum on Linux, md5 -q on macOS)
UNIQUE_SUFFIX=$( (echo -n "$SUBSCRIPTION_ID" | md5sum 2>/dev/null | awk '{print $1}' || echo -n "$SUBSCRIPTION_ID" | md5 -q 2>/dev/null) | head -c6)

SYNAPSE_WORKSPACE_BASE="desafiosynapse"
SYNAPSE_WORKSPACE_NAME="${AZURE_SYNAPSE_WORKSPACE_NAME:-}"
SQL_POOL_NAME="${AZURE_SQL_POOL_NAME:-desafiodw}"
# Use DW100c for Free Trial compatibility (lowest cost)
SQL_POOL_PERFORMANCE_LEVEL="${AZURE_SQL_POOL_PERFORMANCE_LEVEL:-DW100c}"

az account set --subscription "$SUBSCRIPTION_ID"

# --- 4. Resource group ---
log_info "Resource group: checking existence..."
# Check if Resource Group exists (az group exists returns true/false; on permission errors it may not return false per Azure CLI #8594)
EXISTING_RG=$(az group exists -n "$RESOURCE_GROUP" 2>/dev/null || echo "")
if [ "$EXISTING_RG" = "true" ]; then
  log_skip "Resource Group '$RESOURCE_GROUP' already exists"
else
  log_info "Creating Resource Group: $RESOURCE_GROUP"
  az group create --name "$RESOURCE_GROUP" --location "$LOCATION" >/dev/null
  log_ok "Resource Group '$RESOURCE_GROUP' created"
fi

# --- 5. Storage account ---
log_info "Storage account: resolving name and RG..."
# Check if Storage Account exists in our subscription (any resource group)
if [ -z "$STORAGE_ACCOUNT_NAME" ]; then
  EXISTING_SA=$(az storage account list \
    --subscription "$SUBSCRIPTION_ID" \
    --query "[?starts_with(name, '$STORAGE_ACCOUNT_BASE')].{name:name, rg:resourceGroup}" \
    -o tsv 2>/dev/null | head -1)
  
  if [ -n "$EXISTING_SA" ]; then
    STORAGE_ACCOUNT_NAME=$(echo "$EXISTING_SA" | awk '{print $1}')
    EXISTING_RG_SA=$(echo "$EXISTING_SA" | awk '{print $2}')
    log_skip "Found existing Storage Account '$STORAGE_ACCOUNT_NAME' in resource group '$EXISTING_RG_SA'"
  else
    STORAGE_ACCOUNT_NAME="${STORAGE_ACCOUNT_BASE}${UNIQUE_SUFFIX}"
  fi
fi

# RG where the storage account lives (same as ours when we create or reuse from our RG; different when reusing from another RG)
STORAGE_ACCOUNT_RG="${EXISTING_RG_SA:-$RESOURCE_GROUP}"

# Check if this specific storage account exists in our resource group
EXISTING_SA_IN_RG=$(az storage account list \
  --resource-group "$RESOURCE_GROUP" \
  --subscription "$SUBSCRIPTION_ID" \
  --query "[?name=='$STORAGE_ACCOUNT_NAME'].name" \
  -o tsv 2>/dev/null || echo "")

# Create only when: not in our RG AND (we didn't find one in subscription, or the one we found is in our RG)
# When we found in another RG: EXISTING_SA is set, EXISTING_RG_SA != RESOURCE_GROUP → do not create (name would conflict)
if [ -z "$EXISTING_SA_IN_RG" ] && { [ -z "${EXISTING_SA:-}" ] || [ "${EXISTING_RG_SA:-}" = "$RESOURCE_GROUP" ]; }; then
  log_info "Creating Storage Account: $STORAGE_ACCOUNT_NAME"
  az storage account create \
    --name "$STORAGE_ACCOUNT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --sku Standard_LRS \
    --kind StorageV2 \
    --enable-hierarchical-namespace true \
    --min-tls-version TLS1_2 \
    --allow-blob-public-access false \
    --subscription "$SUBSCRIPTION_ID" \
    >/dev/null
else
  log_skip "Storage Account '$STORAGE_ACCOUNT_NAME' already exists"
fi

# --- 6. File system and directories ---
log_info "File system and directories: checking..."
# Check if File System exists (az storage fs exists returns True/False; fallback to show if unavailable)
FS_EXISTS_VAL=$(az storage fs exists -n "$FILE_SYSTEM_NAME" --account-name "$STORAGE_ACCOUNT_NAME" --auth-mode login -o tsv 2>/dev/null || echo "")
if [ "$FS_EXISTS_VAL" = "True" ] || [ "$FS_EXISTS_VAL" = "true" ]; then
  EXISTING_FS="$FILE_SYSTEM_NAME"
else
  EXISTING_FS=$(az storage fs show -n "$FILE_SYSTEM_NAME" --account-name "$STORAGE_ACCOUNT_NAME" --auth-mode login --query "name" -o tsv 2>/dev/null || echo "")
fi

if [ -z "$EXISTING_FS" ]; then
  log_info "Creating File System: $FILE_SYSTEM_NAME"
  set +e
  FS_OUTPUT=$(az storage fs create -n "$FILE_SYSTEM_NAME" --account-name "$STORAGE_ACCOUNT_NAME" --auth-mode login 2>&1)
  FS_RC=$?
  set -e
  if [ $FS_RC -ne 0 ]; then
    log_warn "File system create failed:"
    echo "$FS_OUTPUT"
  else
    log_ok "File System '$FILE_SYSTEM_NAME' created"
  fi
else
  log_skip "File System '$FILE_SYSTEM_NAME' already exists"
fi

# Create directories if they don't exist
log_info "Checking Data Lake directories..."
for dir in "${DIRECTORIES[@]}"; do
  DIR_EXISTS_VAL=$(az storage fs directory exists -f "$FILE_SYSTEM_NAME" -n "$dir" --account-name "$STORAGE_ACCOUNT_NAME" --auth-mode login -o tsv 2>/dev/null || echo "")
  if [ "$DIR_EXISTS_VAL" = "True" ] || [ "$DIR_EXISTS_VAL" = "true" ]; then
    EXISTING_DIR="$dir"
  else
    EXISTING_DIR=$(az storage fs directory show -f "$FILE_SYSTEM_NAME" -n "$dir" --account-name "$STORAGE_ACCOUNT_NAME" --auth-mode login --query "name" -o tsv 2>/dev/null || echo "")
  fi

  if [ -z "$EXISTING_DIR" ]; then
    log_info "Creating directory: $dir"
    set +e
    DIR_OUTPUT=$(az storage fs directory create -f "$FILE_SYSTEM_NAME" -n "$dir" --account-name "$STORAGE_ACCOUNT_NAME" --auth-mode login 2>&1)
    DIR_RC=$?
    set -e
    if [ $DIR_RC -ne 0 ]; then
      log_warn "Directory create failed for $dir:"
      echo "$DIR_OUTPUT"
    fi
  else
    log_skip "Directory '$dir' already exists"
  fi
done

# --- 7. Service principal ---
log_info "Service principal: loading or creating..."
SP_NAME="srag-poc"
STORAGE_ACCOUNT_ID="/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${STORAGE_ACCOUNT_RG}/providers/Microsoft.Storage/storageAccounts/${STORAGE_ACCOUNT_NAME}"

# Reuse SP credentials from .env when AZURE_CLIENT_ID and AZURE_CLIENT_SECRET are set
EXISTING_CLIENT_ID="${AZURE_CLIENT_ID:-}"
EXISTING_CLIENT_SECRET="${AZURE_CLIENT_SECRET:-}"

# Check if Service Principal already exists
EXISTING_SP=$(az ad sp list \
  --display-name "$SP_NAME" \
  --query "[0].appId" \
  -o tsv 2>/dev/null || echo "")

if [ -n "$EXISTING_SP" ]; then
  log_skip "Service Principal '$SP_NAME' already exists"
  
  # Assign Storage Blob Data Contributor to SP on this storage account if not already assigned
  ROLE_ASSIGNMENT=$(az role assignment list \
    --scope "$STORAGE_ACCOUNT_ID" \
    --assignee "$EXISTING_SP" \
    --role "Storage Blob Data Contributor" \
    --query "[0].id" \
    -o tsv 2>/dev/null || echo "")
  
  if [ -z "$ROLE_ASSIGNMENT" ]; then
    log_info "Assigning role to existing Service Principal..."
    az role assignment create \
      --role "Storage Blob Data Contributor" \
      --assignee "$EXISTING_SP" \
      --scope "$STORAGE_ACCOUNT_ID" \
      >/dev/null
  else
    log_skip "Role assignment already exists"
  fi
  
  # Reuse .env secret when valid; otherwise reset SP password and capture new secret
  if [ -n "$EXISTING_CLIENT_SECRET" ] && [ "$EXISTING_CLIENT_SECRET" != "<MANUAL_SETUP_REQUIRED>" ] && [ "$EXISTING_CLIENT_SECRET" != "<CHECK_AZURE_PORTAL_FOR_SECRET>" ]; then
    log_ok "Using existing Service Principal credentials from .env"
    CLIENT_ID="$EXISTING_SP"
    CLIENT_SECRET="$EXISTING_CLIENT_SECRET"
    TENANT_ID=$(az account show --query tenantId -o tsv)
  else
    log_info "Resetting Service Principal credentials (secret not in .env or invalid)..."
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
  log_info "Creating Service Principal: $SP_NAME"
  SP_OUTPUT=$(az ad sp create-for-rbac \
    --name "$SP_NAME" \
    --role "Storage Blob Data Contributor" \
    --scopes "$STORAGE_ACCOUNT_ID" \
    --output json 2>/dev/null)
  
  if [ -z "$SP_OUTPUT" ]; then
    log_err "Error creating Service Principal. Please check your Azure CLI permissions."
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

if [ "$STORAGE_ONLY" != "true" ]; then
# --- 8. Synapse workspace ---
log_info "Synapse workspace: resolving name and credentials..."
SYNAPSE_AVAILABLE=false
SQL_POOL_AVAILABLE=true
# Determine Synapse Workspace name (check for existing or generate unique)
if [ -z "$SYNAPSE_WORKSPACE_NAME" ]; then
  EXISTING_SYNAPSE=$(az synapse workspace list \
    --resource-group "$RESOURCE_GROUP" \
    --query "[?starts_with(name, '$SYNAPSE_WORKSPACE_BASE')].name" \
    -o tsv 2>/dev/null | head -1)
  
  if [ -n "$EXISTING_SYNAPSE" ]; then
    SYNAPSE_WORKSPACE_NAME="$EXISTING_SYNAPSE"
    log_skip "Found existing Synapse Workspace: $SYNAPSE_WORKSPACE_NAME"
  else
    SYNAPSE_WORKSPACE_NAME="${SYNAPSE_WORKSPACE_BASE}${UNIQUE_SUFFIX}"
  fi
fi

# Resolve workspace existence before choosing SQL admin source (recover from workspace vs generate)
EXISTING_WORKSPACE=$(az synapse workspace show \
  --name "$SYNAPSE_WORKSPACE_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "name" \
  -o tsv 2>/dev/null || echo "")

# SQL Admin: prefer .env; else recover from existing workspace; else generate for new workspace
if [ -z "${AZURE_SQL_ADMIN_USER:-}" ]; then
  # Recover sqlAdministratorLogin from existing workspace when not set in .env
  if [ -z "${AZURE_SQL_ADMIN_USER:-}" ] && [ -n "$EXISTING_WORKSPACE" ]; then
    AZURE_SQL_ADMIN_USER=$(az synapse workspace show \
      --name "$SYNAPSE_WORKSPACE_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --query "sqlAdministratorLogin" \
      -o tsv 2>/dev/null || echo "")
    if [ -n "$AZURE_SQL_ADMIN_USER" ]; then
      log_ok "Recovered SQL Admin username from existing workspace: $AZURE_SQL_ADMIN_USER"
    fi
  fi
  
  # Generate new username only when creating a new workspace
  if [ -z "${AZURE_SQL_ADMIN_USER:-}" ] && [ -z "$EXISTING_WORKSPACE" ]; then
    AZURE_SQL_ADMIN_USER="sqladmin${RANDOM}"
  fi
fi

if [ -z "${AZURE_SQL_ADMIN_PASSWORD:-}" ]; then
  # Generate new password only when creating a new workspace; unrecoverable if workspace exists and .env empty
  if [ -z "${AZURE_SQL_ADMIN_PASSWORD:-}" ] && [ -z "$EXISTING_WORKSPACE" ]; then
    # Generate a secure password that meets Azure SQL requirements:
    # - At least 8 characters
    # - Contains uppercase, lowercase, numbers, and special characters
    BASE_PASS=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-12)
    AZURE_SQL_ADMIN_PASSWORD="${BASE_PASS}Aa1!"
  elif [ -z "${AZURE_SQL_ADMIN_PASSWORD:-}" ] && [ -n "$EXISTING_WORKSPACE" ]; then
    log_warn "Workspace exists but AZURE_SQL_ADMIN_PASSWORD not in .env. Set it to the value used when the workspace was created."
    AZURE_SQL_ADMIN_PASSWORD="<PASSWORD_NOT_RECOVERABLE>"
  fi
fi

if [ -n "${AZURE_SQL_ADMIN_USER:-}" ]; then
  SYNAPSE_AVAILABLE=true
  if [ -n "$EXISTING_WORKSPACE" ]; then
    log_skip "Synapse Workspace '$SYNAPSE_WORKSPACE_NAME' already exists"
  else
    log_info "Creating Synapse Workspace: $SYNAPSE_WORKSPACE_NAME"
    set +e
    WORKSPACE_OUTPUT=$(az synapse workspace create \
      --name "$SYNAPSE_WORKSPACE_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --storage-account "$STORAGE_ACCOUNT_NAME" \
      --file-system "$FILE_SYSTEM_NAME" \
      --sql-admin-login-user "$AZURE_SQL_ADMIN_USER" \
      --sql-admin-login-password "$AZURE_SQL_ADMIN_PASSWORD" \
      --location "$LOCATION" \
      --output json 2>&1)
    WRK_RC=$?
    set -e
    if [ $WRK_RC -eq 0 ]; then
      log_ok "Synapse Workspace created successfully"
      log_info "Waiting for workspace to be fully ready..."
      sleep 10
    else
      log_warn "Synapse Workspace creation may have failed; skipping SQL pool, MI, and firewall"
      echo "$WORKSPACE_OUTPUT" | grep -i "error\|failed" || true
      SYNAPSE_AVAILABLE=false
    fi
  fi

  if [ "${SYNAPSE_AVAILABLE}" = "true" ]; then
  # --- 9. SQL pool ---
  log_info "SQL pool: checking existence..."
  SQL_POOL_AVAILABLE=true
  # Check if SQL Pool (Data Warehouse) exists
  EXISTING_SQL_POOL=$(az synapse sql pool show \
    --name "$SQL_POOL_NAME" \
    --workspace-name "$SYNAPSE_WORKSPACE_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "name" \
    -o tsv 2>/dev/null || echo "")

  if [ -n "$EXISTING_SQL_POOL" ]; then
    log_skip "SQL Pool '$SQL_POOL_NAME' already exists"
    # Recover performance level from existing pool (for printed output)
    EXISTING_PERF_LEVEL=$(az synapse sql pool show \
      --name "$SQL_POOL_NAME" \
      --workspace-name "$SYNAPSE_WORKSPACE_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --query "sku.name" \
      -o tsv 2>/dev/null || echo "")
    if [ -n "$EXISTING_PERF_LEVEL" ]; then
      SQL_POOL_PERFORMANCE_LEVEL="$EXISTING_PERF_LEVEL"
      log_ok "Recovered performance level from existing pool: $SQL_POOL_PERFORMANCE_LEVEL"
    fi
  else
    log_info "Creating SQL Pool (Data Warehouse): $SQL_POOL_NAME"
    log_info "Performance Level: $SQL_POOL_PERFORMANCE_LEVEL"
    
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
      log_ok "SQL Pool creation initiated (running in background)"
      log_info "Waiting for pool to be ready..."
      sleep 15
    else
      SQL_POOL_AVAILABLE=false
      log_warn "SQL Pool creation failed; continuing with setup"
      echo "Error details:"
      echo "$SQL_POOL_OUTPUT"
      echo ""
      log_warn "SQL Pool may fail on Free Trial due to quota limits. Create it manually via Azure Portal or retry later."
    fi
  fi

  # --- 10. Synapse MI and firewall ---
  # Get Synapse Workspace details for connection string
  SYNAPSE_SQL_ENDPOINT=$(az synapse workspace show \
    --name "$SYNAPSE_WORKSPACE_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "connectivityEndpoints.sql" \
    -o tsv 2>/dev/null || echo "")

  # Grant Synapse Managed Identity access to Storage Account for COPY INTO
  log_info "Configuring Synapse Managed Identity access to Storage..."
  SYNAPSE_IDENTITY=$(az synapse workspace show \
    --name "$SYNAPSE_WORKSPACE_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "identity.principalId" \
    -o tsv 2>/dev/null || echo "")
  
  if [ -n "$SYNAPSE_IDENTITY" ]; then
    # Skip assignment if Synapse MI already has Storage Blob Data Contributor on this storage account
    SYNAPSE_ROLE=$(az role assignment list \
      --scope "$STORAGE_ACCOUNT_ID" \
      --assignee "$SYNAPSE_IDENTITY" \
      --role "Storage Blob Data Contributor" \
      --query "[0].id" \
      -o tsv 2>/dev/null || echo "")
    
    if [ -z "$SYNAPSE_ROLE" ]; then
      log_info "Assigning Storage Blob Data Contributor to Synapse Managed Identity..."
      az role assignment create \
        --role "Storage Blob Data Contributor" \
        --assignee "$SYNAPSE_IDENTITY" \
        --scope "$STORAGE_ACCOUNT_ID" \
        >/dev/null 2>&1 || log_warn "Could not assign role to Synapse MI (may already exist)"
    else
      log_skip "Synapse Managed Identity already has Storage Blob Data Contributor"
    fi
  fi

  # Configure firewall rule with current client IP
  CURRENT_IP=$(curl -s https://api.ipify.org 2>/dev/null || echo "")
  if [ -n "$CURRENT_IP" ]; then
    log_info "Checking firewall rules for IP: $CURRENT_IP"
    
    # Detect if current IP is already allowed (0.0.0.0 or matching start/end)
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
            log_skip "IP $CURRENT_IP already allowed by firewall rule ($START_IP - $END_IP)"
            break
          fi
        fi
      done <<< "$FIREWALL_RULES"
    fi
    
    if [ "$IP_ALLOWED" = false ]; then
      RULE_NAME="ClientIP_${CURRENT_IP//./_}"
      RULE_EXISTS=$(az synapse workspace firewall-rule show \
        --name "$RULE_NAME" \
        --workspace-name "$SYNAPSE_WORKSPACE_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query "name" -o tsv 2>/dev/null || echo "")
      if [ -n "$RULE_EXISTS" ]; then
        log_skip "Firewall rule '$RULE_NAME' already exists"
      else
        log_info "Adding firewall rule for IP $CURRENT_IP..."
        FIREWALL_OUTPUT=$(az synapse workspace firewall-rule create \
        --resource-group "$RESOURCE_GROUP" \
        --workspace-name "$SYNAPSE_WORKSPACE_NAME" \
        --name "$RULE_NAME" \
        --start-ip-address "$CURRENT_IP" \
        --end-ip-address "$CURRENT_IP" \
        --output json 2>&1)
      
        if [ $? -eq 0 ]; then
          log_ok "Firewall rule added for IP $CURRENT_IP"
        else
          log_warn "Firewall rule creation may have failed"
          echo "$FIREWALL_OUTPUT" | grep -i "error\|failed" || true
          log_warn "Add your IP manually via Azure Portal if needed"
        fi
      fi
    fi
  else
    log_warn "Could not detect current IP; firewall rule not created. Add your IP manually via Azure Portal if needed"
  fi
  fi
fi
else
  log_info "Skipping Synapse (--storage-only): only Storage, SP, key, and SAS will be configured."
  SYNAPSE_AVAILABLE=false
  SYNAPSE_WORKSPACE_NAME=""
fi

# --- 11. Storage key and SAS ---
log_info "Storage key and SAS: retrieving or reusing..."
# Retrieve storage key and generate SAS whenever storage account and file system exist (even if Synapse was skipped)
# Reuse AZURE_STORAGE_KEY and AZURE_STORAGE_SAS_TOKEN from .env when storage account name matches
STORAGE_KEY=""
SAS_TOKEN=""
if [ "${AZURE_STORAGE_ACCOUNT_NAME:-}" = "$STORAGE_ACCOUNT_NAME" ]; then
  STORAGE_KEY="${AZURE_STORAGE_KEY:-}"
  SAS_TOKEN="${AZURE_STORAGE_SAS_TOKEN:-}"
fi
if [ -z "$STORAGE_KEY" ]; then
  log_info "Retrieving Storage Account key for $STORAGE_ACCOUNT_NAME..."
  STORAGE_KEY=$(az storage account keys list \
    --account-name "$STORAGE_ACCOUNT_NAME" \
    --resource-group "$STORAGE_ACCOUNT_RG" \
    --subscription "$SUBSCRIPTION_ID" \
    --query "[0].value" \
    -o tsv 2>/dev/null || echo "")
else
  log_skip "Using AZURE_STORAGE_KEY from .env (storage account matches)"
fi
if [ -z "$SAS_TOKEN" ]; then
  log_info "Generating SAS token for $STORAGE_ACCOUNT_NAME..."
  SAS_EXPIRY=$(date -u -v+1y '+%Y-%m-%dT%H:%MZ' 2>/dev/null || date -u -d '+1 year' '+%Y-%m-%dT%H:%MZ' 2>/dev/null || echo "2026-01-01T00:00Z")
  if [ -n "$STORAGE_KEY" ]; then
    SAS_TOKEN=$(az storage fs generate-sas -n "$FILE_SYSTEM_NAME" --account-name "$STORAGE_ACCOUNT_NAME" --account-key "$STORAGE_KEY" --permissions racwdl --expiry "$SAS_EXPIRY" -o tsv 2>/dev/null || echo "")
    if [ -z "$SAS_TOKEN" ]; then
      SAS_TOKEN=$(az storage container generate-sas --account-name "$STORAGE_ACCOUNT_NAME" --account-key "$STORAGE_KEY" --name "$FILE_SYSTEM_NAME" --permissions racwdl --expiry "$SAS_EXPIRY" --output tsv 2>/dev/null || echo "")
    fi
    if [ -n "$SAS_TOKEN" ]; then
      log_ok "SAS token generated (expires: $SAS_EXPIRY)"
    else
      log_warn "Could not generate SAS token; COPY INTO may not work"
    fi
  fi
else
  log_skip "Using AZURE_STORAGE_SAS_TOKEN from .env (storage account matches)"
fi

# --- 12. Output: print credentials only ---
log_info "Printing credentials to stdout..."
# Print credentials for the user to copy into .env. Use placeholders when Synapse or SQL pool was skipped (Free Trial).
echo
echo "AZURE CREDENTIALS"
echo "=================="
echo "Add these to your .env file:"
echo
echo "SUBSCRIPTION_ID=${SUBSCRIPTION_ID}"
echo "AZURE_TENANT_ID=${TENANT_ID}"
echo "AZURE_CLIENT_ID=${CLIENT_ID}"
echo "AZURE_CLIENT_SECRET=${CLIENT_SECRET}"
echo "STORAGE_ACCOUNT_NAME=${STORAGE_ACCOUNT_NAME}"
echo "FILE_SYSTEM_NAME=${FILE_SYSTEM_NAME}"
echo "AZURE_SYNAPSE_WORKSPACE_NAME=${SYNAPSE_WORKSPACE_NAME:-}"
echo "AZURE_RESOURCE_GROUP=$RESOURCE_GROUP"
if [ "${SYNAPSE_AVAILABLE:-false}" = "true" ] && [ "${SQL_POOL_AVAILABLE:-true}" = "true" ]; then
  echo "AZURE_SQL_POOL_NAME=${SQL_POOL_NAME}"
else
  if [ "${SYNAPSE_AVAILABLE:-false}" = "false" ]; then
    echo "AZURE_SQL_POOL_NAME=<SYNAPSE_NOT_AVAILABLE_FREE_TRIAL>"
  else
    echo "AZURE_SQL_POOL_NAME=<SQL_POOL_QUOTA_FREE_TRIAL>"
  fi
fi
if [ "${SYNAPSE_AVAILABLE:-false}" = "true" ]; then
  echo "AZURE_SYNAPSE_SQL_ENDPOINT=${SYNAPSE_SQL_ENDPOINT:-}"
else
  echo "AZURE_SYNAPSE_SQL_ENDPOINT=<SYNAPSE_NOT_AVAILABLE_FREE_TRIAL>"
fi
if [ "${SYNAPSE_AVAILABLE:-false}" = "true" ]; then
  echo "AZURE_SQL_ADMIN_USER=${AZURE_SQL_ADMIN_USER:-}"
  echo "AZURE_SQL_ADMIN_PASSWORD=${AZURE_SQL_ADMIN_PASSWORD:-}"
else
  echo "AZURE_SQL_ADMIN_USER=<SYNAPSE_NOT_AVAILABLE_FREE_TRIAL>"
  echo "AZURE_SQL_ADMIN_PASSWORD=<SYNAPSE_NOT_AVAILABLE_FREE_TRIAL>"
fi
if [ "${SYNAPSE_AVAILABLE:-false}" = "true" ] && [ "${SQL_POOL_AVAILABLE:-true}" = "true" ]; then
  echo "AZURE_SQL_POOL_PERFORMANCE_LEVEL=${SQL_POOL_PERFORMANCE_LEVEL:-}"
else
  if [ "${SYNAPSE_AVAILABLE:-false}" = "false" ]; then
    echo "AZURE_SQL_POOL_PERFORMANCE_LEVEL=<SYNAPSE_NOT_AVAILABLE_FREE_TRIAL>"
  else
    echo "AZURE_SQL_POOL_PERFORMANCE_LEVEL=<SQL_POOL_QUOTA_FREE_TRIAL>"
  fi
fi
if [ -n "${STORAGE_KEY:-}" ]; then
  echo "AZURE_STORAGE_KEY=${STORAGE_KEY}"
fi
if [ -n "${SAS_TOKEN:-}" ]; then
  echo "AZURE_STORAGE_SAS_TOKEN=${SAS_TOKEN}"
fi
if [ "${SYNAPSE_AVAILABLE:-false}" = "true" ]; then
  echo ""
  echo "--- COST: Dedicated SQL Pool ---"
  echo "Resume/pause is automatic on 'Atualizar Dados'. For manual control, wait until the pool is fully provisioned (provisioningState Succeeded), then:"
  echo "  az synapse sql pool pause --name $SQL_POOL_NAME --workspace-name $SYNAPSE_WORKSPACE_NAME -g $RESOURCE_GROUP"
  echo "  az synapse sql pool resume --name $SQL_POOL_NAME --workspace-name $SYNAPSE_WORKSPACE_NAME -g $RESOURCE_GROUP"
  echo ""
fi
echo
