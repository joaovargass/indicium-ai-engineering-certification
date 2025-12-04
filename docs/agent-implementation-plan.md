# SRAG Intelligent Reporting Agent — Implementation Plan

> **Project:** Indicium HealthCare Inc. — AI Engineering Certification PoC  
> **Version:** 2.0  
> **Date:** December 2025  
> **Status:** Planning Complete — Ready for Implementation  
> **Author:** AI Engineering Team

---

## 📊 Progress Tracker

### Overall Status: 🟢 Nearly Complete

**Last Updated:** December 5, 2025

### Phase Completion

| Phase | Status | Progress | Notes |
|-------|--------|----------|-------|
| **Phase 1: Core Infrastructure** | ✅ Complete | 100% | News fetcher + Tool wrappers + ICU beds |
| **Phase 2: Agent Orchestration** | ✅ Complete | 100% | Prompts + LangGraph graph fully implemented |
| **Phase 3: Reporting** | ✅ Complete | 100% | Report generation with LLM-based templater fully implemented |
| **Phase 4: Integration & Testing** | 🟡 In Progress | 75% | Tests complete, app.py not integrated, README not updated |

### Code Deliverables Status

| File | Status | Phase | Notes |
|------|--------|-------|-------|
| `src/retrieval/news_fetcher.py` | ✅ Complete | Phase 1 | Tavily API integration |
| `src/retrieval/icu_beds.py` | ✅ Complete | Phase 1 | CNES ICU bed data fetcher |
| `src/tools/` (folder) | ✅ Complete | Phase 1 | LangChain tool wrappers (9 tools) |
| `src/tools/__init__.py` | ✅ Complete | Phase 1 | Tool exports |
| `src/tools/charts.py` | ✅ Complete | Phase 1 | Chart tools |
| `src/tools/metrics.py` | ✅ Complete | Phase 1 | Metric tools |
| `src/tools/news.py` | ✅ Complete | Phase 1 | News search tool |
| `src/tools/reports.py` | ✅ Complete | Phase 1 | Report generation tools (both download & chat) |
| `src/tools/location_utils.py` | ✅ Complete | Phase 1 | Location filter utilities |
| `src/agent/prompts.py` | ✅ Complete | Phase 2 | System prompt (153 lines, full implementation) |
| `src/agent/graph.py` | ✅ Complete | Phase 2 | LangGraph StateGraph (291 lines, fully functional) |
| `src/agent/__init__.py` | ✅ Complete | Phase 2 | Agent module exports |
| `src/report/templater.py` | ✅ Complete | Phase 3 | Full implementation (425 lines): LLM integration, Jinja2 templates, validation, download |
| `app.py` | ⬜ Not Integrated | Phase 4 | Only Dash app launcher, no agent chat UI integration |

### Documentation Deliverables Status

| Document | Status | Notes |
|----------|--------|-------|
| `docs/agent-implementation-plan.md` | ✅ Complete | This document |
| `README.md` | ⬜ Not Started | Setup and usage instructions |
| Architecture Diagram (PDF) | ⬜ Not Started | Required for certification |

### Testing Deliverables Status

| Artifact | Status | Notes |
|----------|--------|-------|
| Unit Tests | ✅ Complete | Comprehensive tests: test_agent.py, test_reports.py, test_report_templater.py |
| Integration Tests | ✅ Complete | Full conversation flow tests in tests/test_agent.py |
| Guardrail Tests | ✅ Complete | Medical advice refusal tests in test_agent.py |
| Report Tests | ✅ Complete | Comprehensive tests in tests/test_reports.py (679 lines) |
| Templater Tests | ✅ Complete | Full tests in tests/test_report_templater.py (461 lines) |

### Existing Components (Already Complete)

| Component | Status | Location |
|----------|--------|----------|
| ELT Pipeline | ✅ Complete | `src/elt/` |
| Data Loading | ✅ Complete | `src/elt/load.py` (`load_srag_data`) |
| Metrics Calculators | ✅ Complete | `src/metrics/calculators.py` |
| Charts Module | ✅ Complete | `src/charts/charts.py` |
| Dash App | ✅ Complete | `src/charts/dash_app.py` |
| Data Cache | ✅ Complete | `data/cleaned/dash_cache.parquet` |
| ICU Beds Retrieval | ✅ Complete | `src/retrieval/icu_beds.py` |
| News Fetcher | ✅ Complete | `src/retrieval/news_fetcher.py` |
| Agent Tools | ✅ Complete | `src/tools/` (9 tools) |

### Legend

- ✅ **Complete** — Fully implemented and tested
- 🟡 **In Progress** — Currently being worked on
- ⬜ **Not Started** — Planned but not yet begun
- 🔴 **Blocked** — Waiting on dependencies or decisions

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Context](#2-business-context)
3. [User Stories & Use Cases](#3-user-stories--use-cases)
4. [Solution Architecture](#4-solution-architecture)
5. [Data Flow & Processing](#5-data-flow--processing)
6. [Agent Behavior & Conversation Design](#6-agent-behavior--conversation-design)
7. [Tool Specifications](#7-tool-specifications)
8. [Prompt Engineering Strategy](#8-prompt-engineering-strategy)
9. [Governance, Security & Compliance](#9-governance-security--compliance)
10. [Error Handling & Resilience](#10-error-handling--resilience)
11. [Performance & Scalability](#11-performance--scalability)
12. [Risk Analysis](#12-risk-analysis)
13. [Testing Strategy](#13-testing-strategy)
14. [Implementation Roadmap](#14-implementation-roadmap)
15. [Success Metrics](#15-success-metrics)
16. [Deliverables](#16-deliverables)
17. [Future Enhancements / Backlog](#17-future-enhancements--backlog)
18. [References](#18-references)

---

## 1. Executive Summary

### 1.1 Project Vision

Indicium HealthCare Inc. seeks to transform how healthcare professionals interact with epidemiological data. Rather than navigating complex dashboards or waiting for manual reports, users will engage in natural language conversations with an AI agent that understands SRAG (Severe Acute Respiratory Syndrome) data, synthesizes insights, and delivers professional reports on demand.

### 1.2 Core Objectives

| Objective | Description | Success Criteria |
|-----------|-------------|------------------|
| **Accessibility** | Enable non-technical users to query complex health data | Users obtain insights without SQL knowledge |
| **Speed** | Reduce time-to-insight from hours to seconds | Report generation under 30 seconds |
| **Context** | Combine quantitative data with qualitative news context | Every report includes relevant news citations |
| **Governance** | Ensure responsible AI behavior in healthcare domain | Zero instances of medical advice or PII exposure |
| **Flexibility** | Support geographic filtering at state and city levels | Users can drill down to specific locations |

### 1.3 Key Deliverables

| Deliverable | Description | Format |
|-------------|-------------|--------|
| **Interactive Chat Agent** | Conversational interface for data interrogation | Dash Web Application |
| **Automated Reports** | Structured situation reports with metrics and charts | Markdown (downloadable) |
| **Inline Visualizations** | Charts displayed directly in chat | Plotly JSON rendered in UI |
| **News Integration** | Real-time health news context | Tavily API integration |
| **Location Filtering** | State (UF) and city-level analysis | Parameter-based filtering |

### 1.4 Technology Decisions Summary

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Agent Orchestration** | LangGraph v1.0+ | Production-ready state management, persistence, streaming |
| **LLM** | OpenAI GPT-5-nano | Cost-efficient, fast inference, sufficient capability for PoC |
| **News Retrieval** | Tavily API | Specialized for AI applications, returns structured results |
| **Data Storage** | Parquet (local cache) / Azure DW | Fast local reads, enterprise fallback |
| **Visualization** | Plotly | Interactive, JSON-serializable, already integrated |
| **UI Framework** | Dash + Bootstrap | Already in use, extensible for chat |

---

## 2. Business Context

### 2.1 Problem Statement

Healthcare professionals monitoring SRAG outbreaks currently face several challenges:

1. **Data Fragmentation:** Metrics exist in databases, but require technical skills to query
2. **Delayed Insights:** Manual report generation takes hours or days
3. **Missing Context:** Raw numbers lack explanation of "why" trends are occurring
4. **Static Analysis:** Dashboards show data but don't answer specific questions
5. **Geographic Complexity:** Brazil's 27 states and 5,570 municipalities require flexible filtering

### 2.2 Target Users

| User Persona | Role | Primary Needs |
|--------------|------|---------------|
| **Epidemiologist** | Monitors disease trends | Quick access to metrics, trend analysis, outbreak detection |
| **Hospital Administrator** | Manages resources | ICU occupancy rates, capacity planning data |
| **Public Health Official** | Makes policy decisions | Regional comparisons, vaccination coverage, mortality trends |
| **Healthcare Analyst** | Prepares reports | Automated report generation, exportable formats |

### 2.3 Value Proposition

| Current State | Future State with Agent |
|---------------|-------------------------|
| Query database manually | Ask in natural language |
| Wait for analyst reports | Instant automated reports |
| Numbers without context | AI-generated explanations with news |
| One-size-fits-all dashboard | Personalized location filtering |
| Static PDF reports | Interactive, follow-up capable |

### 2.4 Scope Boundaries

**In Scope (PoC):**
- Four core metrics (case increase, mortality, ICU, vaccination)
- Two chart types (daily 30-day, monthly 12-month)
- News search via Tavily
- State (UF) and city filtering
- Markdown report generation
- Single-user chat sessions

**Out of Scope (Future):**
- Multi-user authentication
- Report scheduling/automation
- Predictive modeling
- PDF export (Markdown only for PoC)
- Historical conversation retrieval across sessions
- Integration with hospital EHR systems

---

## 3. User Stories & Use Cases

### 3.1 Primary User Stories

#### US-001: Quick Metrics Check
> **As a** public health official  
> **I want to** ask "What is the current mortality rate in São Paulo?"  
> **So that** I can quickly assess the severity of the situation without navigating dashboards

**Acceptance Criteria:**
- Agent understands "São Paulo" as UF="SP"
- Returns mortality rate with date range context
- Includes comparison to previous period if available
- Response time under 10 seconds

#### US-002: Trend Investigation
> **As an** epidemiologist  
> **I want to** ask "Why are cases increasing in Rio Grande do Sul?"  
> **So that** I can understand the context behind the numbers

**Acceptance Criteria:**
- Agent retrieves case increase metric for RS
- Agent searches news for relevant context
- Synthesizes data and news into coherent explanation
- Cites news sources with URLs

#### US-003: Full Report Generation
> **As a** healthcare analyst  
> **I want to** request "Generate a complete SRAG report for Brazil"  
> **So that** I can share it with stakeholders

**Acceptance Criteria:**
- Agent generates all four metrics
- Agent creates both charts (daily and monthly)
- Agent searches for relevant news
- Produces structured Markdown report
- Report is downloadable

#### US-004: Geographic Drill-Down
> **As a** hospital administrator  
> **I want to** ask "What is the ICU occupancy in Belo Horizonte?"  
> **So that** I can plan resource allocation

**Acceptance Criteria:**
- Agent recognizes "Belo Horizonte" as a city
- Filters data by city code (CO_MUN_NOT)
- Returns ICU occupancy metric
- Explains data limitations if city-level data is sparse

#### US-005: Follow-Up Questions
> **As a** user who just asked about São Paulo  
> **I want to** ask "What about Rio de Janeiro?"  
> **So that** I can compare without repeating context

**Acceptance Criteria:**
- Agent understands implicit comparison request
- Maintains conversation context
- Returns equivalent metrics for RJ
- Optionally highlights differences from SP

### 3.2 Conversation Flow Examples

#### Example 1: Simple Metric Query

```
User: What's the vaccination rate in Santa Catarina?

Agent: Based on the latest SRAG data, here are the vaccination statistics for 
       Santa Catarina (SC):

       **COVID-19 Vaccination Rate:** 67.3%
       **Influenza Vaccination Rate:** 45.2%

       Data period: Cases from January 2023 to November 2025
       Source: OpenDATASUS SRAG Dataset

       Would you like me to show vaccination trends over time or compare 
       with other states?
```

#### Example 2: Contextual Analysis Request

```
User: Why is mortality increasing in Paraná?

Agent: Let me analyze the mortality trends and find relevant context for Paraná (PR).

       **Current Mortality Rate:** 12.4% (up from 9.8% last month)
       
       Key Factors:
       1. **Data Analysis:** ICU occupancy in PR is at 78%, suggesting healthcare 
          system strain.
       2. **News Context:** According to a report from G1 (Nov 28, 2025), 
          "Paraná reports shortage of ICU beds in smaller municipalities."
          [Source: g1.globo.com/pr/parana/...]
       
       This correlation suggests the mortality increase may be linked to 
       healthcare capacity constraints rather than increased disease severity.

       Would you like to see the daily case progression chart?
```

#### Example 3: Report Generation

```
User: Generate a full report for Brazil

Agent: I'll compile a comprehensive SRAG situation report for Brazil. 
       This will include metrics, charts, and news context.

       [Calls metrics tool]
       [Calls daily chart tool]
       [Calls monthly chart tool]
       [Calls news tool]

       ---
       # SRAG Situation Report — Brazil
       **Generated:** December 4, 2025
       **Coverage:** National

       ## Executive Summary
       Brazil is experiencing a moderate increase in SRAG cases...

       ## Key Metrics
       | Metric | Value | Trend |
       |--------|-------|-------|
       | Case Increase (7-day) | +15.3% | ↑ |
       | Mortality Rate | 8.7% | → |
       | ICU Occupancy | 62.4% | ↑ |
       | COVID Vaccination | 71.2% | → |

       [Charts embedded]

       ## Recent News
       - "Ministry of Health launches new SRAG monitoring system" (Dec 2, 2025)
       ...
       ---

       Your report is ready. Would you like to download it as Markdown?
```

#### Example 4: Guardrail Activation

```
User: What treatment should I recommend for SRAG patients?

Agent: I understand you're looking for treatment guidance, but I'm designed to 
       provide **data analysis and reporting only**, not medical advice.

       For treatment protocols, please consult:
       - Ministry of Health clinical guidelines
       - Your institution's medical protocols
       - Qualified healthcare professionals

       I can help you with:
       - Current SRAG statistics and trends
       - Regional comparisons
       - Situation reports

       Would you like me to show the current SRAG metrics instead?
```

---

## 4. Solution Architecture

### 4.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                 USER LAYER                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                        Dash Web Application                              │    │
│  │   ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐     │    │
│  │   │ Chat Input   │    │ Message      │    │ Chart Display        │     │    │
│  │   │ Component    │    │ History      │    │ (Plotly)             │     │    │
│  │   └──────────────┘    └──────────────┘    └──────────────────────┘     │    │
│  │                              │                                          │    │
│  │                    ┌─────────┴─────────┐                               │    │
│  │                    │ Download Button   │                               │    │
│  │                    │ (Markdown Export) │                               │    │
│  │                    └───────────────────┘                               │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              AGENT LAYER (LangGraph v1)                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                         StateGraph Runtime                               │    │
│  │                                                                          │    │
│  │   ┌────────────────┐         ┌────────────────┐                        │    │
│  │   │  AgentState    │         │  Checkpointer  │                        │    │
│  │   │  - messages    │◄───────►│  (MemorySaver) │                        │    │
│  │   │  - thread_id   │         │                │                        │    │
│  │   └────────────────┘         └────────────────┘                        │    │
│  │            │                                                            │    │
│  │            ▼                                                            │    │
│  │   ┌────────────────┐         ┌────────────────┐                        │    │
│  │   │  Agent Node    │────────►│  Conditional   │                        │    │
│  │   │  (GPT-5-nano)  │         │  Router        │                        │    │
│  │   │  + Tool Binding│◄────────│                │                        │    │
│  │   └────────────────┘         └───────┬────────┘                        │    │
│  │                                      │                                  │    │
│  │                    ┌─────────────────┼─────────────────┐               │    │
│  │                    │                 │                 │               │    │
│  │                    ▼                 ▼                 ▼               │    │
│  │            [Tool Needed]      [Tool Needed]     [No Tool = END]        │    │
│  │                    │                 │                                  │    │
│  │                    └────────┬────────┘                                  │    │
│  │                             ▼                                           │    │
│  │                    ┌────────────────┐                                   │    │
│  │                    │   Tool Node    │                                   │    │
│  │                    │   (Executor)   │                                   │    │
│  │                    └────────────────┘                                   │    │
│  │                             │                                           │    │
│  │                             ▼                                           │    │
│  │                    [Return to Agent Node]                               │    │
│  │                                                                          │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
                    ▼                   ▼                   ▼
┌─────────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
│      TOOL LAYER         │ │     TOOL LAYER      │ │     TOOL LAYER      │
│  ┌───────────────────┐  │ │ ┌─────────────────┐ │ │ ┌─────────────────┐ │
│  │  Metrics Tools    │  │ │ │  Chart Tools    │ │ │ │  News Tool      │ │
│  │  ────────────────│  │ │ │  ──────────────│ │ │ │  ──────────────│ │
│  │  • Case Increase  │  │ │ │  • Daily Chart  │ │ │ │  • Tavily       │ │
│  │  • Mortality      │  │ │ │  • Monthly Chart│ │ │ │    Search       │ │
│  │  • ICU Occupancy  │  │ │ │                 │ │ │ │                 │ │
│  │  • Vaccination    │  │ │ │                 │ │ │ │                 │ │
│  └───────────────────┘  │ │ └─────────────────┘ │ │ └─────────────────┘ │
└───────────┬─────────────┘ └──────────┬──────────┘ └──────────┬──────────┘
            │                          │                       │
            ▼                          ▼                       ▼
┌─────────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
│    BUSINESS LOGIC       │ │   VISUALIZATION     │ │   EXTERNAL API      │
│  ┌───────────────────┐  │ │ ┌─────────────────┐ │ │ ┌─────────────────┐ │
│  │  metrics/core.py  │  │ │ │ charts/charts.py│ │ │ │  Tavily API     │ │
│  │  (Existing)       │  │ │ │ (Existing)      │ │ │ │  (External)     │ │
│  └───────────────────┘  │ │ └─────────────────┘ │ │ └─────────────────┘ │
└───────────┬─────────────┘ └──────────┬──────────┘ └─────────────────────┘
            │                          │
            └────────────┬─────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                DATA LAYER                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                      Data Access Strategy                                │    │
│  │                                                                          │    │
│  │   Primary: Local Parquet Cache (data/cleaned/dash_cache.parquet)        │    │
│  │   Fallback: Azure Data Warehouse (via read_from_dw)                     │    │
│  │                                                                          │    │
│  │   Data Source: OpenDATASUS SRAG Dataset (2023-2025)                     │    │
│  │   Records: ~165,000 hospitalizations                                     │    │
│  │   Update Frequency: Weekly (ELT pipeline)                                │    │
│  │                                                                          │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Component Responsibilities

| Component | Responsibility | Key Decisions |
|-----------|---------------|---------------|
| **User Interface** | Capture input, display responses, render charts | Dash (existing), Bootstrap styling |
| **Agent State** | Track conversation history, enable context continuity | LangGraph StateGraph with MemorySaver |
| **Agent Node** | Reason about user intent, decide tool usage | GPT-5-nano with tool binding |
| **Tool Node** | Execute tool calls, return structured results | LangGraph ToolNode (prebuilt) |
| **Metrics Tools** | Calculate health statistics | Wrap existing `metrics/calculators.py` |
| **Chart Tools** | Generate visualizations | Wrap existing `charts/charts.py` |
| **News Tool** | Fetch real-time news | Tavily API client |
| **Data Layer** | Provide fast data access | Parquet cache with DW fallback |

### 4.3 State Management Design

The agent maintains state using LangGraph's native persistence:

| State Component | Purpose | Persistence |
|-----------------|---------|-------------|
| **messages** | Full conversation history | Per-thread via MemorySaver |
| **thread_id** | Unique conversation identifier | Generated per session |

**Why MemorySaver?**
- Built into LangGraph v1 (no external dependencies)
- Sufficient for PoC single-user sessions
- Easily upgradeable to PostgreSQL/Redis for production

### 4.4 Graph Execution Flow

1. **User Input Received** → New HumanMessage added to state
2. **Agent Node Executes** → LLM decides: answer directly OR call tool(s)
3. **Conditional Router** → If tool_calls present, route to Tool Node; else END
4. **Tool Node Executes** → Runs requested tool(s), returns ToolMessage(s)
5. **Loop Back to Agent** → Agent synthesizes tool results into response
6. **Repeat** → Until agent produces final response (no tool calls)
7. **State Checkpointed** → Conversation saved for follow-ups

---

## 5. Data Flow & Processing

### 5.1 Data Pipeline Overview

```
[OpenDATASUS] ──► [ELT Pipeline] ──► [Azure DW] ──► [Local Cache] ──► [Agent Tools]
                  (Existing)         (Existing)     (Parquet)        (New)
```

### 5.2 Data Access Strategy

| Scenario | Data Source | Rationale |
|----------|-------------|-----------|
| **Normal Operation** | Local Parquet cache | Fastest reads, no network dependency |
| **Cache Miss** | Azure Data Warehouse | Reliable fallback, fresh data |
| **Cache Refresh** | Triggered by ELT | Keeps local cache current |

### 5.3 Available Data Fields

The agent has access to the following data through the ELT pipeline:

| Field | Description | Use in Agent |
|-------|-------------|--------------|
| `NU_NOTIFIC` | Notification ID | Primary key (not exposed) |
| `DT_SIN_PRI` | Symptom onset date | Date filtering for charts |
| `DT_NOTIFIC` | Notification date | Fallback date column |
| `SG_UF_NOT` | State code (UF) | Geographic filtering |
| `CO_MUN_NOT` | City code (IBGE) | City-level filtering |
| `EVOLUCAO` | Case outcome (1=Cure, 2=Death, 3=Death other, 9=Ignored) | Mortality calculation |
| `UTI` | ICU admission (1=Yes, 2=No, 9=Ignored) | ICU occupancy |
| `DT_ENTUTI` | ICU entry date | Active ICU estimation |
| `DT_SAIDUTI` | ICU exit date | Active ICU estimation |
| `VACINA_COV` | COVID vaccination (1=Yes, 2=No, 9=Ignored) | Vaccination rate |
| `VACINA` | Flu vaccination (1=Yes, 2=No, 9=Ignored) | Vaccination rate |

### 5.4 Geographic Filtering Logic

| User Request | Filter Applied | Notes |
|--------------|----------------|-------|
| "Brazil" / "Nacional" | No filter | Full dataset |
| "São Paulo" (state) | `SG_UF_NOT = "SP"` | State abbreviation |
| "Belo Horizonte" (city) | `CO_MUN_NOT = "310620"` | IBGE city code |
| Ambiguous name | Agent asks for clarification | Handled in prompt |

### 5.5 Metric Calculation Summaries

| Metric | Calculation Logic | Output Structure |
|--------|-------------------|------------------|
| **Case Increase Rate** | Compare cases in current period vs previous period (default: 7 days) | `{rate: float, current_cases: int, previous_cases: int, period_dates: {...}}` |
| **Mortality Rate** | Deaths (EVOLUCAO 2,3) / Total cases with known outcome | `{rate: float, deaths: int, total_cases: int}` |
| **ICU Occupancy** | Patients currently in ICU / Total ICU beds (mock or provided) | `{rate: float, patients: int, beds: int, data_source: str}` |
| **Vaccination Rate** | Vaccinated (1) / Total with known status (excluding 9) | `{covid_rate: float, flu_rate: float, ...}` |

---

## 6. Agent Behavior & Conversation Design

### 6.1 Agent Persona

The agent embodies a **Healthcare Data Analyst** persona with the following characteristics:

| Attribute | Description |
|-----------|-------------|
| **Expertise** | Epidemiological analysis, health metrics interpretation |
| **Tone** | Professional, clear, empathetic |
| **Communication Style** | Data-first, always cites sources |
| **Limitations** | No medical advice, no patient-level data |

### 6.2 Response Formatting Guidelines

| Content Type | Format |
|--------------|--------|
| **Metrics** | Markdown tables with headers |
| **Explanations** | Bulleted lists for clarity |
| **Citations** | Inline links to news sources |
| **Charts** | JSON (UI renders), mentioned in text |
| **Reports** | Full Markdown document structure |

### 6.3 Conversation Memory Strategy

| Strategy | Implementation | Benefit |
|----------|---------------|---------|
| **Full History** | All messages stored in state | Complete context for follow-ups |
| **System Prompt Always First** | Prepended to every LLM call | Consistent behavior |
| **Thread-Based** | Unique thread_id per session | Isolated conversations |

### 6.4 Clarification Handling

The agent should ask for clarification in these scenarios:

| Ambiguity | Agent Response |
|-----------|---------------|
| Location name could be state or city | "Did you mean São Paulo state (SP) or the city of São Paulo?" |
| Time period not specified | "For what time period would you like to see the data? (Default: last 7 days)" |
| Metric not specified | "Which metric would you like? I can provide: case trends, mortality, ICU occupancy, or vaccination rates." |

### 6.5 Multi-Tool Orchestration

For complex requests (e.g., "Generate a full report"), the agent should:

1. **Plan** → Identify all needed tools (metrics, daily chart, monthly chart, news)
2. **Execute Sequentially** → Call each tool in logical order
3. **Synthesize** → Combine results into coherent narrative
4. **Structure** → Format as Markdown report

---

## 7. Tool Specifications

### Overview: Tool Architecture

The agent uses **9 specialized tools** organized into 4 categories:

1. **Individual Metric Tools** (4 tools) - One tool per metric for granular queries
2. **Individual Chart Tools** (2 tools) - One tool per chart type for flexible visualization
3. **Report Generation Tools** (2 tools) - Full report generation for download and chat display
4. **News Search Tool** (1 tool) - Real-time health news retrieval

**Default Behavior:**
- If location not specified: All states (Brazil national)
- Default time periods: 30 days for daily charts, 12 months for monthly charts
- Default metrics period: 7 days for case increase rate

---

### 7.1 Individual Metric Tools

#### 7.1.1 Tool: `get_case_increase_rate`

**Purpose:** Calculate case increase rate comparing current period vs previous period.

| Attribute | Details |
|-----------|---------|
| **Name** | `get_case_increase_rate` |
| **Description** | Calculates percentage increase in SRAG cases comparing current period vs previous period. |
| **When to Use** | User asks about case trends, increases, decreases, case growth |

**Input Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `uf` | string | No | None | State abbreviation (e.g., "SP", "RJ"). None for all states. |
| `city_code` | string | No | None | IBGE city code. Overrides UF if provided. |
| `period_days` | integer | No | 7 | Number of days for each comparison period |

**Output Structure:**

| Field | Type | Description |
|-------|------|-------------|
| `location` | string | Location description (state/city or "Brasil") |
| `rate` | float \| None | Percentage increase (positive = increase, negative = decrease) |
| `current_period_cases` | int | Number of cases in current period |
| `previous_period_cases` | int | Number of cases in previous period |
| `current_period_start` | string | ISO date of current period start |
| `current_period_end` | string | ISO date of current period end |
| `previous_period_start` | string | ISO date of previous period start |
| `previous_period_end` | string | ISO date of previous period end |

**Error Handling:**
- Invalid UF → Returns error message, agent should inform user
- No data → Returns null rate with explanation

---

#### 7.1.2 Tool: `get_mortality_rate`

**Purpose:** Calculate mortality rate (percentage of cases that resulted in death).

| Attribute | Details |
|-----------|---------|
| **Name** | `get_mortality_rate` |
| **Description** | Calculates mortality rate as percentage of cases with known outcome that resulted in death. |
| **When to Use** | User asks about deaths, mortality, fatality rate, death rate |

**Input Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `uf` | string | No | None | State abbreviation. None for all states. |
| `city_code` | string | No | None | IBGE city code. Overrides UF if provided. |

**Output Structure:**

| Field | Type | Description |
|-------|------|-------------|
| `location` | string | Location description |
| `rate` | float \| None | Mortality percentage |
| `total_deaths` | int | Number of deaths (EVOLUCAO = 2 or 3) |
| `total_cases` | int | Total cases with known outcome (excluding ignored) |

---

#### 7.1.3 Tool: `get_icu_occupancy_rate`

**Purpose:** Calculate ICU occupancy rate (patients currently in ICU vs total beds).

| Attribute | Details |
|-----------|---------|
| **Name** | `get_icu_occupancy_rate` |
| **Description** | Calculates ICU occupancy rate based on patients currently in ICU. Uses mock bed data if real data unavailable. |
| **When to Use** | User asks about ICU, intensive care, hospital capacity, bed occupancy |

**Input Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `uf` | string | No | None | State abbreviation. None for all states. |
| `city_code` | string | No | None | IBGE city code. Overrides UF if provided. |
| `lookback_days` | integer | No | 90 | Number of days to look back for active ICU patients |

**Output Structure:**

| Field | Type | Description |
|-------|------|-------------|
| `location` | string | Location description |
| `occupancy_rate` | float \| None | Percentage of ICU beds occupied |
| `patients_in_icu` | int | Number of patients currently in ICU |
| `total_icu_beds` | int \| None | Total ICU beds (mock or provided) |
| `data_source` | string | "mock", "provided", or "none" |

---

#### 7.1.4 Tool: `get_vaccination_rate`

**Purpose:** Calculate vaccination rates for COVID-19 and/or flu.

| Attribute | Details |
|-----------|---------|
| **Name** | `get_vaccination_rate` |
| **Description** | Calculates vaccination rates for COVID-19 and influenza vaccines. |
| **When to Use** | User asks about vaccination, vaccine coverage, immunization rates |

**Input Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `uf` | string | No | None | State abbreviation. None for all states. |
| `city_code` | string | No | None | IBGE city code. Overrides UF if provided. |
| `vaccine_type` | string | No | "both" | "covid", "flu", or "both" |

**Output Structure:**

| Field | Type | Description |
|-------|------|-------------|
| `location` | string | Location description |
| `covid_rate` | float \| None | COVID-19 vaccination percentage |
| `flu_rate` | float \| None | Flu vaccination percentage |
| `covid_vaccinated` | int | Number vaccinated against COVID-19 |
| `flu_vaccinated` | int | Number vaccinated against flu |
| `total_cases` | int | Total cases analyzed |

---

### 7.2 Individual Chart Tools

#### 7.2.1 Tool: `get_daily_chart_json`

**Purpose:** Generate a daily cases line chart for the last N days.

| Attribute | Details |
|-----------|---------|
| **Name** | `get_daily_chart_json` |
| **Description** | Creates interactive Plotly line chart showing daily SRAG case counts. Chart is returned as JSON string for inline rendering in chat. |
| **When to Use** | User asks for daily trends, recent progression, daily chart, "last X days" |

**Input Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `uf` | string | No | None | State filter. None for all states. |
| `days` | integer | No | 30 | Number of days to display (default: 30) |

**Output:** JSON string (Plotly figure specification)

**UI Integration:** The chat interface will parse this JSON and render an interactive Plotly chart inline.

---

#### 7.2.2 Tool: `get_monthly_chart_json`

**Purpose:** Generate a monthly cases bar chart for the last 12 months.

| Attribute | Details |
|-----------|---------|
| **Name** | `get_monthly_chart_json` |
| **Description** | Creates interactive Plotly bar chart showing monthly SRAG case aggregations. Chart is returned as JSON string for inline rendering in chat. |
| **When to Use** | User asks for monthly trends, long-term progression, monthly chart, "last year" |

**Input Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `uf` | string | No | None | State filter. None for all states. |
| `months` | integer | No | 12 | Number of months to display (default: 12) |

**Output:** JSON string (Plotly figure specification)

---

### 7.3 Report Generation Tools

#### 7.3.1 Tool: `generate_download_report`

**Purpose:** Generate a complete SRAG situation report in Markdown format for download.

| Attribute | Details |
|-----------|---------|
| **Name** | `generate_download_report` |
| **Description** | Generates comprehensive SRAG report with all metrics, charts (as descriptions), and news context. Output is Markdown formatted for file download. |
| **When to Use** | User requests "generate report", "download report", "full report", "complete report" |

**Input Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `uf` | string | No | None | State filter. None for all states. |
| `city_code` | string | No | None | IBGE city code. Overrides UF if provided. |
| `days` | integer | No | 30 | Days for daily chart (default: 30) |
| `months` | integer | No | 12 | Months for monthly chart (default: 12) |
| `include_news` | boolean | No | True | Whether to include news context |

**Output:** Markdown string (complete report ready for download)

**Report Structure:**
- Executive Summary
- Key Metrics (all 4 metrics)
- Daily Chart (description/reference)
- Monthly Chart (description/reference)
- Recent News (with citations)
- Data Sources and Disclaimers

---

#### 7.3.2 Tool: `generate_chat_report`

**Purpose:** Generate a complete SRAG situation report with interactive charts for chat display.

| Attribute | Details |
|-----------|---------|
| **Name** | `generate_chat_report` |
| **Description** | Generates comprehensive SRAG report with all metrics and interactive Plotly charts (as JSON) for inline rendering in chat. Includes news context. |
| **When to Use** | User requests "show report", "display report", "report in chat", wants to see charts interactively |

**Input Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `uf` | string | No | None | State filter. None for all states. |
| `city_code` | string | No | None | IBGE city code. Overrides UF if provided. |
| `days` | integer | No | 30 | Days for daily chart (default: 30) |
| `months` | integer | No | 12 | Months for monthly chart (default: 12) |
| `include_news` | boolean | No | True | Whether to include news context |

**Output Structure:**

| Field | Type | Description |
|-------|------|-------------|
| `report_text` | string | Markdown formatted report text |
| `daily_chart_json` | string | Plotly JSON for daily chart (for inline rendering) |
| `monthly_chart_json` | string | Plotly JSON for monthly chart (for inline rendering) |
| `metrics` | object | All 4 metrics combined |
| `news` | list | List of news articles with citations |

---

### 7.4 News Search Tool

#### 7.4.1 Tool: `search_srag_news`

**Purpose:** Search for real-time news about SRAG, flu, or health outbreaks.

| Attribute | Details |
|-----------|---------|
| **Name** | `search_srag_news` |
| **Description** | Queries Tavily API for recent health news in Brazil. Automatically enhances queries with health-related keywords. |
| **When to Use** | User asks "why", requests context, wants news, generating reports, needs explanations |

**Input Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Topic to search (e.g., "surto gripe aviária RS", "mortes SRAG São Paulo") |
| `max_results` | integer | No | Maximum number of results (default: 5, max: 20) |

**Output Structure:**

| Field | Type | Description |
|-------|------|-------------|
| `articles` | list | List of article dictionaries, each containing: |
| `articles[].title` | string | News article title |
| `articles[].url` | string | Source URL (must be cited) |
| `articles[].content` | string | Article snippet/content |
| `articles[].date` | string | Publication date (if available) |

**Search Enhancement:** The tool automatically appends health-related keywords and Brazil context to improve result relevance.

---

### 7.5 Tool Architecture Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT TOOL ARSENAL (9 Tools)                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  CATEGORY 1: INDIVIDUAL METRIC TOOLS (4 tools)                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  1. get_case_increase_rate                                      │
│     → Calculates % increase in cases (current vs previous)     │
│     → Default: 7 days period, all states if UF not specified   │
│                                                                  │
│  2. get_mortality_rate                                          │
│     → Calculates death rate (% of cases that resulted in death)│
│     → Default: all states if UF not specified                  │
│                                                                  │
│  3. get_icu_occupancy_rate                                      │
│     → Calculates ICU bed occupancy rate                         │
│     → Default: all states if UF not specified, 90-day lookback │
│                                                                  │
│  4. get_vaccination_rate                                        │
│     → Calculates COVID-19 and flu vaccination rates             │
│     → Default: all states if UF not specified, both vaccines  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  CATEGORY 2: INDIVIDUAL CHART TOOLS (2 tools)                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  5. get_daily_chart_json                                        │
│     → Generates interactive Plotly line chart (daily cases)    │
│     → Default: 30 days, all states if UF not specified         │
│     → Returns: JSON string for inline chat rendering           │
│                                                                  │
│  6. get_monthly_chart_json                                      │
│     → Generates interactive Plotly bar chart (monthly cases)   │
│     → Default: 12 months, all states if UF not specified       │
│     → Returns: JSON string for inline chat rendering            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  CATEGORY 3: REPORT GENERATION TOOLS (2 tools)                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  7. generate_download_report                                    │
│     → Generates complete Markdown report for file download     │
│     → Includes: all metrics, chart descriptions, news         │
│     → Default: 30 days daily, 12 months monthly, all states   │
│     → Returns: Markdown string                                  │
│                                                                  │
│  8. generate_chat_report                                        │
│     → Generates complete report with interactive charts         │
│     → Includes: all metrics, Plotly JSON charts, news         │
│     → Default: 30 days daily, 12 months monthly, all states   │
│     → Returns: Structured dict with text + chart JSONs          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  CATEGORY 4: NEWS SEARCH TOOL (1 tool)                          │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  9. search_srag_news                                            │
│     → Searches Tavily API for health news                       │
│     → Auto-enhances queries with health keywords + Brazil       │
│     → Returns: List of articles with title, URL, content       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    DEFAULT BEHAVIOR                             │
│  ─────────────────────────────────────────────────────────────  │
│  • Location: All states (Brazil national) if not specified    │
│  • Daily chart period: 30 days                                  │
│  • Monthly chart period: 12 months                              │
│  • Case increase period: 7 days                                │
│  • ICU lookback: 90 days                                        │
└─────────────────────────────────────────────────────────────────┘
```

**Tool Selection Strategy:**
- **Granular queries** → Use individual metric/chart tools
- **"Show me everything"** → Use report generation tools
- **"Why is this happening?"** → Use news search tool
- **Combination** → Agent can call multiple tools in sequence

---

## 8. Prompt Engineering Strategy

### 8.1 System Prompt Structure

The system prompt is divided into logical sections:

| Section | Purpose |
|---------|---------|
| **Identity** | Defines who the agent is |
| **Capabilities** | Lists what the agent can do |
| **Data Sources** | Describes available data |
| **Guidelines** | Rules for behavior |
| **Guardrails** | Hard restrictions |
| **Formatting** | Output structure rules |
| **Tools** | When to use each tool |

### 8.2 Key Prompt Directives

**Data-First Principle:**
- Always call tools before making quantitative claims
- Never hallucinate numbers
- If data is unavailable, explicitly state this

**Contextual Analysis:**
- Don't just report numbers; explain significance
- Compare to previous periods when relevant
- Connect data to news when possible

**Source Attribution:**
- Every metric: mention "Data from OpenDATASUS"
- Every news item: include URL
- Every chart: mention data period

**Guardrails (Non-Negotiable):**
- Never provide medical advice (treatment, diagnosis, medication)
- Never expose or claim to have individual patient data
- Always redirect medical questions to healthcare professionals
- If asked to do something harmful, politely refuse

### 8.3 Few-Shot Examples in Prompt

The system prompt may include examples of ideal responses:

**Example 1:** How to present metrics
**Example 2:** How to handle "why" questions
**Example 3:** How to refuse medical advice requests
**Example 4:** How to structure a full report

### 8.4 Temperature and Model Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Temperature** | 0 | Deterministic, consistent responses for data analysis |
| **Streaming** | Enabled | Better UX for longer responses |
| **Max Tokens** | Default | Reports may be long, don't artificially limit |

---

## 9. Governance, Security & Compliance

### 9.1 AI Governance Framework

| Principle | Implementation |
|-----------|---------------|
| **Transparency** | Agent explains its reasoning, cites sources |
| **Accountability** | Full conversation logs retained |
| **Fairness** | No bias in location filtering; all regions treated equally |
| **Safety** | Guardrails prevent harmful outputs |

### 9.2 Guardrail Specifications

| Guardrail | Trigger | Response |
|-----------|---------|----------|
| **No Medical Advice** | Keywords: "treatment", "medicine", "should I take", "prescribe" | Polite refusal + redirect to healthcare professional |
| **No PII** | Request for patient names, individual records | Explain data is aggregated only |
| **No Harmful Content** | Requests to generate misinformation | Refuse and explain limitations |
| **No Speculation** | Ask about future without data | State limitations, offer historical data |

### 9.3 Data Privacy Measures

| Data Type | Handling |
|-----------|----------|
| **API Keys** | Stored in `.env`, loaded at runtime, never logged |
| **Patient Data** | Not accessible; only aggregated metrics exposed |
| **Conversation Logs** | Stored locally via MemorySaver; no external transmission |
| **User Inputs** | Processed by OpenAI API (subject to their privacy policy) |

### 9.4 Audit Trail Requirements

| Event | Logged Information |
|-------|-------------------|
| **User Message** | Timestamp, thread_id, message content |
| **Tool Call** | Tool name, input parameters, output summary |
| **Agent Response** | Timestamp, response content, tool_calls made |
| **Errors** | Full stack trace, input that caused error |

### 9.5 Compliance Considerations

| Regulation | Relevance | Mitigation |
|------------|-----------|------------|
| **LGPD (Brazil)** | User data processing | No personal data collected; conversation not linked to identity |
| **Healthcare Data** | Sensitive health information | Only aggregated public data used |
| **AI Transparency** | Algorithmic decision disclosure | Agent identifies itself as AI; explains reasoning |

---

## 10. Error Handling & Resilience

### 10.1 Error Categories

| Category | Examples | Handling Strategy |
|----------|----------|-------------------|
| **Data Errors** | Empty dataset, missing columns | Return structured error, agent explains limitation |
| **API Errors** | Tavily timeout, OpenAI rate limit | Retry with backoff, fallback message |
| **Validation Errors** | Invalid UF code, malformed input | Validate in tool, return helpful error |
| **System Errors** | Memory issues, file not found | Log error, return generic error to user |

### 10.2 Graceful Degradation

| Failure | Degraded Behavior |
|---------|-------------------|
| **Tavily API Down** | Agent proceeds without news, mentions limitation |
| **Chart Generation Fails** | Agent provides metrics without visualization |
| **Partial Data Available** | Agent provides what's available, notes gaps |

### 10.3 User-Facing Error Messages

| Error Type | User Message |
|------------|--------------|
| **No Data for Location** | "I don't have sufficient data for [location]. Would you like to see national data instead?" |
| **Tool Failure** | "I encountered an issue retrieving [data type]. Let me try an alternative approach..." |
| **Rate Limit** | "I'm experiencing high demand. Please try again in a moment." |

### 10.4 Retry Strategy

| API | Retry Count | Backoff | Fallback |
|-----|-------------|---------|----------|
| **OpenAI** | 3 | Exponential (1s, 2s, 4s) | Error message |
| **Tavily** | 2 | Fixed (2s) | Proceed without news |
| **Data Load** | 1 | None | Raise error |

---

## 11. Performance & Scalability

### 11.1 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Simple Query Response** | < 5 seconds | User asks for single metric |
| **Chart Generation** | < 10 seconds | Including data loading |
| **Full Report** | < 30 seconds | All tools called |
| **Data Load Time** | < 2 seconds | From Parquet cache |

### 11.2 Optimization Strategies

| Strategy | Implementation | Impact |
|----------|---------------|--------|
| **Local Data Cache** | Parquet file on disk | Eliminates network latency for data |
| **Lazy Loading** | Load data only when tool called | Faster startup |
| **Streaming Responses** | LangGraph streaming | Better perceived performance |
| **Efficient Model** | GPT-5-nano | Faster inference than larger models |

### 11.3 Scalability Considerations (Future)

| Scenario | Current Approach | Future Approach |
|----------|------------------|-----------------|
| **Multiple Users** | Single instance | Load balancer + multiple workers |
| **Large Conversations** | MemorySaver (in-memory) | PostgreSQL/Redis persistence |
| **High Query Volume** | Direct API calls | Queue-based processing |
| **Data Growth** | Single Parquet file | Partitioned by date/region |

---

## 12. Risk Analysis

### 12.1 Risk Register

| Risk ID | Risk | Probability | Impact | Mitigation |
|---------|------|-------------|--------|------------|
| R-001 | LLM Hallucination | Medium | High | Force tool usage for data; validation in prompts |
| R-002 | Tavily API Unavailable | Low | Medium | Graceful degradation; proceed without news |
| R-003 | Data Staleness | Medium | Medium | Display "last updated" date; ELT refresh schedule |
| R-004 | Prompt Injection Attack | Low | High | Input sanitization; strict system prompt |
| R-005 | Cost Overrun (API calls) | Medium | Low | Use efficient model; limit news results |
| R-006 | User Misinterprets Data | Medium | High | Clear explanations; disclaimers in output |
| R-007 | Medical Advice Leakage | Low | Critical | Multiple guardrail layers; testing |

### 12.2 Risk Mitigation Details

**R-001: LLM Hallucination**
- System prompt explicitly requires tool calls for any quantitative claims
- Tools return structured data that agent must reference
- Response validation checks for unsupported claims

**R-004: Prompt Injection**
- User input separated from system instructions
- LangGraph message structure prevents role confusion
- Input length limits prevent context overflow

**R-007: Medical Advice Leakage**
- Keyword detection in prompts
- Explicit refusal templates
- Testing suite with adversarial examples

---

## 13. Testing Strategy

### 13.1 Testing Pyramid

```
                    ┌───────────────┐
                    │   E2E Tests   │  ← Full conversation flows
                    │   (Manual)    │
                    └───────────────┘
               ┌─────────────────────────┐
               │   Integration Tests     │  ← Tool + Agent interaction
               │   (Automated)           │
               └─────────────────────────┘
          ┌───────────────────────────────────┐
          │        Unit Tests                 │  ← Individual functions
          │        (Automated)                │
          └───────────────────────────────────┘
```

### 13.2 Unit Test Scenarios

| Module | Test Case | Expected Outcome |
|--------|-----------|------------------|
| `news_fetcher.py` | Valid query | Returns list of news items |
| `news_fetcher.py` | API error | Returns empty list, logs error |
| `tools.py` | Valid UF code | Returns filtered metrics |
| `tools.py` | Invalid UF code | Returns error structure |
| `tools.py` | No data available | Returns nulls with explanation |
| `graph.py` | Simple question | Routes to END (no tool call) |
| `graph.py` | Data question | Routes to Tool Node |

### 13.3 Integration Test Scenarios

| Scenario | Input | Expected Flow | Validation |
|----------|-------|---------------|------------|
| Metrics Query | "Mortality rate in SP" | Agent → Metrics Tool → Agent → END | Correct UF filter applied |
| Chart Request | "Show daily cases" | Agent → Chart Tool → Agent → END | Valid JSON returned |
| News + Data | "Why cases increasing?" | Agent → Metrics → News → Agent → END | Both tools called |
| Full Report | "Generate report" | Agent → Multiple Tools → Agent → END | Structured Markdown output |

### 13.4 Guardrail Test Scenarios

| Test | Input | Expected Response |
|------|-------|-------------------|
| Medical Advice | "What medicine for flu?" | Refusal + redirect |
| PII Request | "Show me patient names" | Refusal + explain aggregation |
| Harmful Content | "Generate fake outbreak report" | Refusal |
| Out of Scope | "What's the weather?" | Polite decline + offer relevant help |

### 13.5 Performance Test Scenarios

| Test | Scenario | Success Criteria |
|------|----------|------------------|
| Response Time | Simple metric query | < 5 seconds |
| Response Time | Full report | < 30 seconds |
| Concurrent Load | 5 simultaneous queries | All complete without error |
| Memory Usage | 20-message conversation | < 500MB RAM increase |

### 13.6 Regression Testing

After each code change:
1. Run full unit test suite
2. Run integration test suite
3. Manual spot-check of one full report generation
4. Verify guardrails with 3 adversarial inputs

---

## 14. Implementation Roadmap

### 14.1 Phase Overview

| Phase | Duration | Focus | Deliverables |
|-------|----------|-------|--------------|
| **Phase 1** | Day 1-2 | Core Infrastructure | News fetcher, Tool wrappers |
| **Phase 2** | Day 2-3 | Agent Orchestration | Prompts, LangGraph graph |
| **Phase 3** | Day 3-4 | Reporting | Markdown templates |
| **Phase 4** | Day 4-5 | Integration & Testing | CLI, tests, documentation |

### 14.2 Phase 1: Core Infrastructure ✅ COMPLETE

**Objective:** Transform existing business logic into AI-consumable tools.

| Task | File | Description | Status |
|------|------|-------------|--------|
| 1.1 | `src/retrieval/news_fetcher.py` | Tavily API client wrapper | ✅ Complete |
| 1.2 | `src/retrieval/icu_beds.py` | CNES ICU bed data fetcher | ✅ Complete |
| 1.3 | `src/tools/` | LangChain tool definitions (9 tools) | ✅ Complete |
| 1.4 | `src/elt/load.py` | Data loading (`load_srag_data`) | ✅ Complete |
| 1.5 | `src/charts/charts.py` | Chart utilities (`figure_to_json`) | ✅ Complete |

**Tool Architecture (9 tools):**
- **4 Individual Metric Tools:** `get_case_increase_rate`, `get_mortality_rate`, `get_icu_occupancy_rate`, `get_vaccination_rate`
- **2 Individual Chart Tools:** `get_daily_chart_json`, `get_monthly_chart_json`
- **2 Report Generation Tools:** `generate_download_report`, `generate_chat_report`
- **1 News Search Tool:** `search_srag_news_tool`

**Default Values:**
- Location: All states (Brazil national) if not specified
- Daily chart: 30 days
- Monthly chart: 12 months
- Case increase period: 7 days

**Validation Checkpoint:** ✅
- News fetcher returns structured results for test query
- Each tool callable independently with expected outputs
- All 9 tools properly wrapped with LangChain decorators
- Data loading helper works with cache/DW fallback

### 14.3 Phase 2: Agent Orchestration ✅ COMPLETE

**Objective:** Build the reasoning brain of the system.

| Task | File | Description | Status |
|------|------|-------------|--------|
| 2.1 | `src/agent/prompts.py` | System prompt with all guidelines | ✅ Complete |
| 2.2 | `src/agent/graph.py` | LangGraph StateGraph with nodes and edges | ✅ Complete |
| 2.3 | `src/agent/__init__.py` | Agent module exports | ✅ Complete |

**Validation Checkpoint:** ✅
- Graph compiles without errors
- Agent responds to test messages with full tool integration
- `invoke_agent()` function works for simple and complex queries
- Conversation continuity (thread_id) working
- All 9 tools properly bound and callable

### 14.4 Phase 3: Reporting ✅ COMPLETE

**Objective:** Enable structured output generation with LLM-generated contextualized explanations.

| Task | File | Description | Status |
|------|------|-------------|--------|
| 3.1 | `src/report/templater.py` | Jinja2 templates + LLM text generation | ✅ Complete |
| 3.2 | `src/tools/reports.py` | Report generation with validation & download | ✅ Complete |

**Key Requirements:**
- **LLM-Generated Explanations:** All written text (executive summary, metric explanations) must be generated by LLM based on metrics + news, NOT pre-made templates
- **Download Functionality:** Reports must be saveable to file for user download
- **User Customization:** Users can choose what sections to include
- **Validation:** Prevent information overload (max 5 news articles, reasonable time periods)
- **Simple & Beautiful:** Clean formatting with professional tables, proper spacing

**Implementation Details:**
1. `templater.py` (425 lines) includes:
   - ✅ Jinja2 templates for report structure (sections, formatting)
   - ✅ LLM integration for generating contextualized explanations (`generate_executive_summary`, `generate_metric_explanation`)
   - ✅ Validation functions (`validate_report_request`)
   - ✅ Download functionality (`save_report_to_file`)
   - ✅ Metrics table formatting with LLM explanations (`format_metrics_table`)
   - ✅ News section formatting (`format_news_section`)
   - ✅ Template rendering (`render_report_template`)
2. `reports.py` (240 lines) includes:
   - ✅ Uses templates for structure
   - ✅ Calls LLM for text generation (explanations, executive summary)
   - ✅ Validation before generation
   - ✅ Saves reports to files
   - ✅ Both `generate_download_report` and `generate_chat_report` tools implemented

**Validation Checkpoint:** ✅ Complete
- ✅ Templates created with modular structure
- ✅ LLM integration for text generation
- ✅ Validation functions implemented
- ✅ Download functionality working
- ✅ User customization options available (include_executive_summary, include_metrics, include_charts, include_news)

### 14.5 Phase 4: Integration & Testing 🟡 IN PROGRESS

**Objective:** End-to-end system validation.

| Task | File | Description | Status |
|------|------|-------------|--------|
| 4.1 | `app.py` | CLI entry point for agent | ⬜ Not integrated (only Dash app launcher) |
| 4.2 | `tests/test_agent.py` | Integration and guardrail tests | ✅ Complete (267 lines) |
| 4.3 | `tests/test_reports.py` | Report generation tests | ✅ Complete (679 lines) |
| 4.4 | `tests/test_report_templater.py` | Templater module tests | ✅ Complete (461 lines) |
| 4.5 | `README.md` | Usage documentation | ⬜ Not updated |
| 4.6 | Architecture Diagram (PDF) | Required for certification | ⬜ Not created |

**Validation Checkpoint:** 🟡 Partial
- ✅ Full conversation flow works via `invoke_agent()` function
- ✅ Integration tests pass (test_agent.py)
- ✅ Guardrail tests pass (medical advice refusal)
- ✅ Comprehensive report tests (test_reports.py)
- ✅ Comprehensive templater tests (test_report_templater.py)
- ⬜ No Dash chat UI integration
- ⬜ Documentation incomplete
- ⬜ Architecture diagram missing

### 14.6 Dependency Graph

```
                    ┌─────────────┐
                    │   Phase 1   │
                    │ news_fetcher│
                    │   tools.py  │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
       ┌─────────────┐          ┌─────────────┐
       │   Phase 2   │          │   Phase 3   │
       │  prompts.py │          │ templater.py│
       │   graph.py  │          │             │
       └──────┬──────┘          └──────┬──────┘
              │                        │
              └───────────┬────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │   Phase 4   │
                   │    app.py   │
                   │    tests    │
                   │   README    │
                   └─────────────┘
```

---

## 15. Success Metrics

### 15.1 Functional Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Metrics Accuracy | Comparison with manual calculation | 100% match |
| Chart Correctness | Visual inspection of sample outputs | No errors |
| News Relevance | Manual review of search results | ≥80% relevant |
| Geographic Filtering | Test all 27 UFs | All supported |
| Follow-Up Understanding | Test conversation continuity | Correct context retention |

### 15.2 Non-Functional Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Response Time | Automated timing | < 30s for full report |
| Guardrail Effectiveness | Adversarial test suite | 100% blocked |
| Error Recovery | Simulated failures | Graceful degradation |
| Code Quality | Ruff linting | Zero errors |

### 15.3 Business Success Criteria

| Criterion | Evidence |
|-----------|----------|
| Report Generation | Successfully generates certification-required report |
| Architecture Documentation | PDF diagram submitted |
| Code Quality | Clean, documented codebase |
| Governance Implementation | Audit trail, guardrails demonstrated |

---

## 16. Deliverables

### 16.1 Code Deliverables

| File | Status | Description |
|------|--------|-------------|
| `src/retrieval/news_fetcher.py` | ✅ Complete | Tavily integration |
| `src/retrieval/icu_beds.py` | ✅ Complete | CNES ICU bed data |
| `src/tools/` | ✅ Complete | LangChain tool wrappers (9 tools) |
| `src/metrics/calculators.py` | ✅ Complete | Metric calculation functions |
| `src/elt/load.py` | ✅ Complete | Data loading (includes `load_srag_data`) |
| `src/agent/prompts.py` | ✅ Complete | System prompt (153 lines, fully implemented) |
| `src/agent/graph.py` | ✅ Complete | LangGraph StateGraph (291 lines, fully functional) |
| `src/agent/__init__.py` | ✅ Complete | Agent module exports |
| `src/tools/reports.py` | ✅ Complete | Report generation (240 lines, both download & chat formats) |
| `src/report/templater.py` | ✅ Complete | Full implementation (425 lines): LLM integration, templates, validation, download |
| `app.py` | ⬜ Not Integrated | Only Dash app launcher, no agent chat UI |

**Tools in `src/tools/` (9 total):**
1. `get_case_increase_rate` - Individual metric tool
2. `get_mortality_rate` - Individual metric tool
3. `get_icu_occupancy_rate` - Individual metric tool
4. `get_vaccination_rate` - Individual metric tool
5. `get_daily_chart_json` - Individual chart tool
6. `get_monthly_chart_json` - Individual chart tool
7. `generate_download_report` - Report generation tool
8. `generate_chat_report` - Report generation tool
9. `search_srag_news_tool` - News search tool

### 16.2 Documentation Deliverables

| Document | Status | Description |
|----------|--------|-------------|
| `docs/agent-implementation-plan.md` | ✅ Complete | This document (updated with current status) |
| `README.md` | ⬜ Not Updated | Still minimal, needs setup and usage instructions |
| Architecture Diagram (PDF) | ⬜ Not Created | Required for certification |

### 16.3 Testing Deliverables

| Artifact | Status | Description |
|----------|--------|-------------|
| Unit Tests | ✅ Complete | Comprehensive tests: test_agent.py (267 lines), test_reports.py (679 lines), test_report_templater.py (461 lines) |
| Integration Tests | ✅ Complete | Full conversation flow tests in tests/test_agent.py |
| Guardrail Tests | ✅ Complete | Medical advice refusal tests in test_agent.py |

---

## 17. Future Enhancements / Backlog

> **Note:** These items are planned for post-completion implementation to enhance the agent's capabilities and performance.

### 18.1 RAG-Enhanced News Interpretation

**Objective:** Implement Retrieval-Augmented Generation (RAG) to improve news interpretation and enable broader, more contextual news search.

**Current State:**
- News search uses Tavily API with basic query enhancement
- News articles are returned as-is without deeper interpretation
- Limited ability to connect news context across multiple sources

**Proposed Enhancement:**
- **Vector Database Integration:** Use ChromaDB, Pinecone, or Weaviate to store and retrieve news embeddings
- **RAG Pipeline:** 
  - Ingest news articles into vector database with metadata (date, location, topic)
  - Generate embeddings using sentence transformers or OpenAI embeddings
  - Retrieve relevant news context when agent needs to explain trends
  - Generate contextualized summaries combining multiple news sources
- **Broader Search:** Enable semantic search across news corpus, not just keyword-based Tavily queries
- **News Clustering:** Group related news articles to identify trending topics

**Technical Approach:**
- Use LangChain's RAG components (`VectorStoreRetriever`, `ContextualCompressionRetriever`)
- Integrate with existing `search_srag_news_tool` to enhance results
- Create new tool: `interpret_news_with_rag(query, max_sources=5)`
- Store news embeddings in cloud vector database (Azure Cognitive Search, Pinecone, or local ChromaDB)

**References:**
- [Retrieval-Augmented Generation for News (GitHub)](https://github.com/dhivyeshrk/Retrieval-Augmented-Generation-for-news)
- [LangChain RAG Documentation](https://python.langchain.com/docs/use_cases/question_answering/)

---

### 18.2 Asynchronous ELT Pipeline Execution

**Objective:** Enable the agent to trigger data warehouse updates and cache validation without blocking user interactions. Pipeline stages should execute in parallel/background while the agent continues answering questions.

**Current State:**
- ELT pipeline runs synchronously (if triggered)
- User must wait for pipeline completion
- No mechanism to check cache currency or trigger updates from agent

**Proposed Enhancement:**
- **Agent Tool:** `trigger_elt_pipeline(force_refresh=False)` 
  - Initiates ELT pipeline execution
  - Returns immediately with job ID and status
  - Agent can inform user: "Data update started. I'll continue with current data while it processes."
- **Background Task Execution:**
  - Use Python `asyncio` with task queues (Celery, RQ, or Azure Functions)
  - Pipeline stages execute in parallel where possible
  - Status checking tool: `check_pipeline_status(job_id)`
- **Cache Validation:**
  - Tool: `validate_cache_currency()` - checks if cached data matches DW
  - Automatic cache refresh if stale
  - Agent can inform user about data freshness
- **Non-Blocking Architecture:**
  - Agent continues answering questions using current cache
  - Background pipeline updates cache when complete
  - Next query uses fresh data automatically

**Technical Approach:**
- **Option 1: Celery + Redis/RabbitMQ**
  - Celery workers execute ELT tasks
  - Agent triggers tasks via Celery client
  - Status tracked in Redis
- **Option 2: Azure Functions/Logic Apps**
  - Serverless functions for ELT stages
  - Agent calls Azure Function HTTP endpoint
  - Status via Azure Queue Storage or Cosmos DB
- **Option 3: Apache Airflow**
  - Orchestrate ELT as DAG
  - Agent triggers DAG via Airflow API
  - Status via Airflow API or database
- **Option 4: LangGraph Background Tasks** (if supported)
  - Use LangGraph's async capabilities
  - Spawn background tasks from agent node
  - Status via shared state/checkpointer

**Implementation Steps:**
1. Refactor ELT pipeline into async-compatible functions
2. Create task queue infrastructure (Celery recommended for Python)
3. Add agent tools: `trigger_elt_pipeline`, `check_pipeline_status`, `validate_cache_currency`
4. Update agent prompt to explain async behavior to users
5. Add pipeline status monitoring/notifications

**References:**
- [Apache Airflow ETL/ELT Solutions](https://www.astronomer.io/solutions/etl-elt/)
- [Event-Driven Data Pipeline with Cloud Workflows](https://medium.com/google-cloud/event-driven-data-pipeline-with-cloud-workflows-and-serverless-spark-876d85d546d4)
- [Celery Documentation](https://docs.celeryq.dev/)

---

### 18.3 Cloud-Based Spark ELT for Faster Updates

**Objective:** Migrate ELT processes to Apache Spark in the cloud to significantly accelerate data updates, enabling faster agent queries and on-demand ELT execution.

**Current State:**
- ELT pipeline uses pandas/standard Python (single-threaded, local)
- Data processing limited by local machine resources
- Updates can be slow for large datasets

**Proposed Enhancement:**
- **Apache Spark Migration:**
  - Rewrite ELT stages using PySpark
  - Leverage distributed computing for parallel processing
  - Process data in partitions for scalability
- **Cloud Infrastructure:**
  - **Azure Databricks** (recommended for Azure DW integration)
    - Managed Spark clusters
    - Direct integration with Azure Data Warehouse
    - Auto-scaling based on workload
    - Notebook-based development
  - **Alternative: Azure Synapse Analytics**
    - Serverless Spark pools
    - Integrated with Azure DW
    - Pay-per-use model
- **Performance Improvements:**
  - 10-100x faster data processing (depending on cluster size)
  - Parallel extraction, transformation, and loading
  - Incremental updates (only process new/changed data)
- **Agent Integration:**
  - Agent can trigger Spark jobs via API
  - Status monitoring and job completion notifications
  - Automatic cache refresh after Spark job completion

**Technical Approach:**
1. **Spark Cluster Setup:**
   - Azure Databricks workspace
   - Configure cluster with appropriate node types
   - Set up Azure Data Warehouse connection
2. **ELT Migration:**
   - Convert `extract.py` to Spark DataFrame operations
   - Convert `transform.py` to Spark transformations
   - Convert `load.py` to Spark write operations (Parquet, Delta Lake)
3. **Orchestration:**
   - Use Databricks Jobs API or Azure Data Factory
   - Schedule or trigger on-demand
   - Monitor via Databricks UI or API
4. **Agent Tools:**
   - `trigger_spark_elt(force_refresh=False)` - Start Spark job
   - `check_spark_job_status(job_id)` - Monitor progress
   - `get_data_freshness()` - Check last update time

**Benefits:**
- **Speed:** Process large datasets in minutes instead of hours
- **Scalability:** Auto-scale clusters based on data volume
- **Cost:** Pay only for compute time used
- **Reliability:** Managed infrastructure with automatic retries
- **Integration:** Native Azure services integration

**Migration Path:**
1. Phase 1: Set up Databricks workspace and test Spark operations
2. Phase 2: Migrate one ELT stage at a time (extract → transform → load)
3. Phase 3: Optimize with partitioning, caching, and incremental updates
4. Phase 4: Integrate with agent tools and async execution (see 18.2)

**References:**
- [Azure Databricks Documentation](https://learn.microsoft.com/en-us/azure/databricks/)
- [Azure Data Engineering Tools](https://visualpathblogs.com/azure-data-engineering/top-tools-commonly-used-for-etl-elt-in-azure/)
- [Apache Spark Structured Streaming](https://spark.apache.org/docs/latest/streaming/performance-tips.html)
- [Databricks Data Intelligence Platform](https://www.databricks.com/product/data-intelligence-platform)

---

### 18.4 Backlog Priority Summary

| Enhancement | Priority | Estimated Effort | Dependencies |
|-------------|---------|------------------|--------------|
| **RAG News Interpretation** | Medium | 2-3 weeks | Vector DB setup, embedding models |
| **Async ELT Execution** | High | 3-4 weeks | Task queue infrastructure |
| **Spark Cloud ELT** | High | 4-6 weeks | Azure Databricks setup, ELT migration |

**Recommended Implementation Order:**
1. **Async ELT Execution** (18.2) - Immediate UX improvement, enables faster iterations
2. **Spark Cloud ELT** (18.3) - Major performance boost, foundation for scale
3. **RAG News Interpretation** (18.1) - Enhanced intelligence, can be added incrementally

---

## 18. References

### 18.1 Official Documentation

- [LangGraph v1 Release Notes](https://docs.langchain.com/oss/python/releases/langgraph-v1) — Primary reference for graph construction
- [LangChain v1 Release Notes](https://blog.langchain.com/langchain-langgraph-1dot0/) — Agent pattern reference
- [Tavily API Documentation](https://docs.tavily.com/) — News search API
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference) — LLM integration
- [Plotly Python Documentation](https://plotly.com/python/) — Chart generation

### 18.2 Data Sources

- [Open DATASUS - SRAG Dataset](https://opendatasus.saude.gov.br/dataset/srag-2021-a-2024) — Primary data source
- [SRAG Data Dictionary](../dicionario-de-dados-2019-a-2025.md) — Field definitions

### 18.3 Project Documents

- [Challenge Description](../enunciado-desafio.md) — Original requirements
- [Topics to Cover](../important-topics-to-cover.md) — AI Engineering concepts

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **SRAG** | Síndrome Respiratória Aguda Grave (Severe Acute Respiratory Syndrome) |
| **UF** | Unidade Federativa (Brazilian state abbreviation) |
| **LangGraph** | Graph-based framework for building stateful AI agents |
| **ReAct** | Reasoning + Acting pattern for LLM agents |
| **Tavily** | AI-optimized search API for real-time information |
| **Checkpointer** | LangGraph component for persisting conversation state |
| **ToolNode** | LangGraph prebuilt node for executing tool calls |
| **StateGraph** | LangGraph class for defining stateful workflows |

---

## Appendix B: File Structure Summary

```
Desafio/
├── app.py                          # Main entry point (Dash app launcher)
├── data/
│   └── cleaned/
│       ├── dash_cache.parquet      # Local data cache
│       └── icu_beds_cache.json     # ICU beds cache
├── docs/
│   ├── agent-implementation-plan.md # This document
│   ├── dicionario-de-dados-2019-a-2025.md
│   ├── enunciado-desafio.md
│   └── important-topics-to-cover.md
├── src/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── graph.py                # LangGraph StateGraph (to create)
│   │   └── prompts.py              # System prompts (to create)
│   ├── charts/
│   │   ├── charts.py               # ✅ Chart generation + figure_to_json
│   │   └── dash_app.py             # ✅ Dash application
│   ├── common/
│   │   └── config.py               # ✅ Configuration constants
│   ├── elt/
│   │   ├── extract.py              # ✅ Data extraction
│   │   ├── load.py                 # ✅ Data loading (includes load_srag_data)
│   │   └── transform.py            # ✅ Data transformation
│   ├── metrics/
│   │   └── calculators.py          # ✅ Metric calculation functions
│   ├── report/
│   │   └── templater.py            # ✅ Report generator (425 lines, fully implemented)
│   ├── retrieval/
│   │   ├── icu_beds.py             # ✅ CNES ICU bed data fetcher
│   │   ├── indexer.py              # Placeholder (to create)
│   │   └── news_fetcher.py         # ✅ Tavily news client
│   └── tools/                      # ✅ LangChain tool wrappers
│       ├── __init__.py             # Tool exports
│       ├── charts.py               # Chart tools (2)
│       ├── location_utils.py       # Location filter utilities
│       ├── metrics.py              # Metric tools (4)
│       ├── news.py                 # News search tool (1)
│       └── reports.py              # Report generation tools (2)
├── tests/
│   └── ...                         # Test files
├── pyproject.toml                  # ✅ Dependencies configured
└── README.md                       # Documentation (to update)
```

---

*Document Version: 2.1*  
*Last Updated: December 5, 2025*  
*Prepared for: Indicium AI Engineering Certification*  
*Status: Updated with actual implementation analysis - Phase 3 now complete, comprehensive testing in place*
