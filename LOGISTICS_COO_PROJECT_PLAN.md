# Logistics COO Copilot — Project Plan

Date: 2026-03-19  
Project: Manager (Logistics industry)  
Goal: Build a production-style COO assistant that monitors logistics operations, explains risks, and recommends actions.

---

## 1) Product Vision (MVP)

Build a **Logistics COO Command Center** where chat is only one part of the UI.

The app should:
- Monitor operational health (fleet, SLA, delay risk, cost trends).
- Detect issues and prioritize actions.
- Use tools and external agents (including hosted RAG) to ground decisions.
- Show evidence for every recommendation.

---

## 2) Target Users

- COO / Head of Operations
- Regional Operations Managers
- Dispatch / Control Tower Leads

---

## 3) Core Agent Architecture

### A) Orchestrator Agent (existing base, extend)
Responsibilities:
- Understand user intent.
- Decide whether to answer directly or call tools.
- Route to specialist tools/agents.
- Synthesize final response with action items.

### B) Specialist Capability Layers (as tools first)
Start as tools; later promote to separate agents if complexity grows:
1. **SLA & Delay Analysis**
2. **Fleet Utilization Analysis**
3. **Cost & Margin Analysis**
4. **Exception Triage**
5. **RAG Policy/Playbook Lookup** (external DO hosted RAG)

### C) Tool Execution Loop
Keep current pattern:
- `llm_reasoning` decides tool call(s)
- `tool_execution` executes tools
- loop until final answer

---

## 4) Data and Tooling Strategy

## 4.1 Immediate (MVP Demo Data)
Use mock datasets + small local JSON/CSV for:
- shipments
- vehicles
- routes
- delivery SLA events
- fuel/ops costs

## 4.2 External Integrations (phase-wise)
- Telemetry API (vehicle status, ETA)
- TMS/ERP API (orders, costs)
- External DO RAG agent for SOPs/contracts/policy docs

## 4.3 Tool Categories
1. **Operational tools** (e.g., delay summary, lane bottlenecks)
2. **Financial tools** (cost per shipment, margin by route)
3. **Knowledge tools** (RAG lookups for SOP and policy)
4. **Action tools** (create escalation, assign owner, set due date)

---

## 5) UI Plan (Beyond Chat)

MVP panels:
1. **KPI Header Strip**
   - On-time delivery %
   - Active delays
   - Fleet utilization
   - Cost per shipment
   - Gross margin trend

2. **Risk & Alerts Panel**
   - Severity: Critical / High / Medium
   - Grouped by region / lane / customer

3. **Action Board**
   - Recommended actions from agent
   - Owner, ETA, status, confidence

4. **Chat + Evidence Drawer**
   - Chat for ad-hoc analysis
   - Evidence drawer: which tools/agent outputs were used

5. **Scenario Widget (simple)**
   - What-if controls (fuel +10%, demand +15%, vehicle downtime)

---

## 6) MVP Scope (Fast Build)

### In Scope
- Single orchestrator with robust tool-calling loop
- 6 to 8 logistics tools (mix of mock + 1 external RAG tool)
- Dashboard with KPI strip + alerts + action board + chat
- Basic auditability (tool selected logs + evidence in response)

### Out of Scope (for now)
- Full autonomous workflows with approvals
- Complex RBAC and enterprise SSO
- Real-time streaming event pipeline

---

## 7) Execution Plan (Task Breakdown)

## Phase 0 — Stabilize Current Core (0.5 day)
- Freeze current working loop.
- Add smoke tests for: no-tool answer, single-tool call, multi-step tool loop.
- Standardize env loading through helper utils.

Deliverable:
- Stable baseline branch for logistics implementation.

## Phase 1 — Logistics Domain Model + Mock Data (1 day)
- Define canonical data schemas for shipments, fleets, routes, events.
- Create clean seed dataset (`data/logistics_mock/*.json`).
- Build first tools against mock data.

Deliverable:
- Deterministic tool outputs for common COO questions.

## Phase 2 — Logistics Tool Pack (1–2 days)
Implement tools:
1. `get_delay_risk_summary`
2. `get_on_time_rate_by_region`
3. `get_fleet_utilization`
4. `get_lane_bottlenecks`
5. `get_cost_per_shipment`
6. `get_top_exceptions`
7. `ask_external_rag_agent` (already started; repurpose for logistics policy)

Deliverable:
- Tool registry with clear descriptions and schema.

## Phase 3 — Reasoning and Routing Quality (1 day)
- Improve system prompt and routing hints for logistics tasks.
- Add response contract:
  - summary
  - risks
  - recommended actions
  - evidence

Deliverable:
- Consistent COO-style answers with action orientation.

## Phase 4 — Dashboard UI MVP (1–2 days)
- Build command center layout with 4 key panels.
- Wire chat + tool/evidence outputs.
- Add simple refresh and filter controls.

Deliverable:
- Usable demo UI beyond plain chatbot.

## Phase 5 — External RAG + Knowledge Base (1 day)
- Connect logistics SOP docs via DO hosted RAG agent.
- Validate retrieval relevance with 15–20 test queries.
- Add citation/evidence snippet in response.

Deliverable:
- Policy-grounded decision support.

## Phase 6 — Demo Hardening (0.5–1 day)
- Add guardrails for unknown/unsafe actions.
- Add timeout/retry/error messaging for external tools.
- Prepare scripted demo scenarios.

Deliverable:
- Reliable demo build ready for presentation.

---

## 8) Suggested Folder Expansion (When ready)

- `src/agent/` orchestrator + node logic
- `src/tools/` tool implementations + registry
- `src/domain/` logistics schemas and transforms
- `src/data/` mock seed data loaders
- `src/ui/` dashboard app
- `src/evals/` regression prompts + expected behavior

---

## 9) Key Metrics for Success

- Tool-call accuracy for logistics queries
- Action recommendation usefulness
- SLA risk detection precision
- Avg response latency
- % responses with evidence

---

## 10) What I Need From You (Input Checklist)

To move from plan to execution, provide:
1. **Logistics subdomain** (3PL, last-mile, freight forwarding, cold chain, etc.)
2. **Top 5 KPIs** your COO cares about most
3. **Top 5 recurring operational problems**
4. **Initial SOP/Policy docs** for RAG ingestion
5. **Preferred UI stack** (React/Next, Streamlit, etc.)

---

## 11) First Build Sprint (Immediate Next Tasks)

Task 1: Define logistics mock schema and 50 sample records  
Task 2: Replace experimental actor/city tools with first 3 logistics tools  
Task 3: Update system routing hint to logistics context  
Task 4: Add response format with `summary + risks + actions + evidence`  
Task 5: Build minimal KPI + alert panel prototype

---

This plan is designed to reuse your current architecture and ship fast while remaining extensible for real production integrations.
