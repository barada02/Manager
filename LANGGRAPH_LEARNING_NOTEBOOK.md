# LangGraph Learning Notebook

Date: 2026-03-18  
Goal: Learn LangGraph part by part, build code modularly, and keep practical notes.

---

## How we’ll learn (modular path)

- [ ] Module 0: Setup and environment check
- [ ] Module 1: LangGraph basics (State, Nodes, Edges)
- [ ] Module 2: Build first minimal graph
- [ ] Module 3: Add branching and conditional routing
- [ ] Module 4: Memory and conversation state
- [ ] Module 5: Tool-calling node(s)
- [ ] Module 6: Multi-step workflow orchestration
- [ ] Module 7: Debugging, tracing, and best practices
- [ ] Module 8: Mini project (end-to-end)

---

## Core concepts (quick notes)

### 1) State
- Shared data object passed between nodes.
- Each node reads/writes part of state.

### 2) Node
- A function that transforms state.
- Usually one clear responsibility per node.

### 3) Edge
- Connection between nodes.
- Defines control flow (what runs next).

### 4) Conditional edge
- Route to different nodes based on state values.

### 5) START / END
- Entry and exit points of the workflow graph.

---

## Module 1: LangGraph basics (State, Nodes, Edges)

### Learning target
Understand what each building block does before adding complexity.

### 1) State (data contract)
- State is a shared dictionary-like object.
- In Python, we define it with `TypedDict` for clarity.
- Every node receives current state and returns updated fields.

### 2) Nodes (single responsibility)
- A node is just a Python function.
- Keep each node focused on one transformation.
- Input: state, Output: partial/full state update.

### 3) Edges (flow control)
- Edges define execution order between nodes.
- `START` marks where graph execution begins.
- `END` marks completion.

### Module 1 run file
- `modules/module_1_basics/minimal_graph.py`

### Module 1 checklist
- [ ] Read the file and identify State, Node functions, and Edges.
- [ ] Run it once and inspect output.
- [ ] Change input message and rerun.
- [ ] Explain in your own words: why StateGraph is useful.

### Stop rule
Do not proceed to Module 2 until all checklist items above are clear.

---

## Session Log

### Session 1 (Today)
- Created this notebook.
- Created virtual environment (`venv`).
- Next: Setup Python env + install LangGraph, then run first tiny graph.

---

## Module 0: Setup and environment check (Windows)

### Step 0.1 Activate venv (PowerShell)
```powershell
.\venv\Scripts\Activate.ps1
```

If activation is blocked, run once in current PowerShell session:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### Step 0.2 Upgrade pip + install packages
```powershell
python -m pip install --upgrade pip
pip install langgraph langchain-core
```

### Step 0.3 Verify environment
```powershell
python modules/module_0_setup/check_env.py
```

Expected: Python details + `LangGraph: installed`

### Step 0.4 Run first minimal graph (Module 1 preview)
```powershell
python modules/module_1_basics/minimal_graph.py
```

Expected output includes:
```text
{'message': 'LangGraph says: hello from module 1 🚀'}
```

---

## Code Snippets (we’ll fill incrementally)

### Snippet A: First graph skeleton
```python
# (to be added in Module 2)
```

### Snippet B: Conditional routing
```python
# (to be added in Module 3)
```

### Snippet C: Memory example
```python
# (to be added in Module 4)
```

---

## Questions / Doubts

- 

---

## Next action

Install dependencies from `requirements.txt`, then complete Module 1 checklist only.
