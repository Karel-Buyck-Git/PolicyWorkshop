Moving your agentic flow from a static Markdown instruction set to a Python-driven orchestration layer is a significant upgrade. It shifts the burden of "state management" from the LLM's context window to your local compute environment.

By using **Claude Code** to generate the backbone, you can create a modular system where Python handles the heavy lifting (searching files, calculating deltas) and the LLM handles the high-level reasoning.

---

## 1. The Dynamic Orchestration Architecture

Instead of feeding the LLM the entire policy repo, Python will act as a **Resource Provider**.

### Core Components

- **The Orchestrator (`main.py`):** Coordinates the flow between the Git repo, the filters, and the LLM calls.
- **Git Manager (`git_handler.py`):** Handles daily pulls and extracts commit history to find "deltas" (new or modified policies).
- **Policy Engine (`policy_processor.py`):** Parses JSON policy definitions, maps them to your "Essential/Professional/Enterprise" tiers, and enforces guardrails.
- **Manifest (`config.yaml`):** Stores the "MVP Default Values," Tier mappings, and job parameters.

---

## 2. Implementing the "Sales Pitch" Taxonomy

To make this work for a Microsoft Valued Partner (MVP) offering, the Python script should categorize policies based on your proprietary metadata.

### The Tiering Logic

You can define your tiers in a YAML structure that the Python script references:

```yaml
tiers:
  essential:
    description: "Baseline security and cost hygiene"
    tags: ["Security Center", "Tagging", "Allowed Regions"]
  professional:
    description: "Operational excellence and compliance"
    tags: ["Backup", "Monitoring", "Network Isolation"]
  enterprise:
    description: "High-scale governance and automation"
    tags: ["Private Link", "Dedicated Clusters", "Sentinel"]
```

---

## 3. Python Orchestration Workflow

Here is how you should prompt **Claude Code** to generate the specific modules:

### Phase A: The Git Delta Logic

> _Claude, write a Python script using `GitPython` that identifies all `.json` files in the `built-in-policies` folder changed within the last 24 hours. Output a list of policy IDs and their 'Description' fields._

### Phase B: Filtering and Constraints

> _Create a filter function that takes an array of Azure service names (e.g., `['CosmosDB', 'SQL']`) and matches them against the `policyRule` logic in the Azure Policy JSON files. Ensure the script ignores 'Deprecated' policies._

### Phase C: Enrichment and Output

> _Write a function that merges the filtered policies with our `config.yaml` metadata. It should assign a 'Tier' and 'MVP Default Value' to each. Finally, render this into a Markdown table using a Jinja2 template._

---

## 4. Addressing Context & Speed Constraints

To prevent the LLM from hitting context limits:

1. **Summarization:** Don't send the whole Policy JSON to the LLM. Let Python extract the `displayName`, `description`, and `parameters`.
2. **Chunking:** If you have 500 matching policies, have Python process them in batches of 20, generating one table section at a time.
3. **State Persistence:** Use a local SQLite database or a JSON file to track which policies have already been "pitched" or reviewed to avoid redundant processing.

---

## 5. Future-Proofing for EPAC & API

By moving to Python now, you are building the "Service Layer" for your future UI.

| Future Feature             | Implementation Path                                                                            |
| -------------------------- | ---------------------------------------------------------------------------------------------- |
| **UI for Business**        | Use **Streamlit** or **FastAPI + React** to visualize the Python-generated Markdown tables.    |
| **API Read Functions**     | Turn your `policy_processor.py` functions into endpoints using **FastAPI**.                    |
| **Self-Service Lifecycle** | Use **GitHub Actions** to trigger your Python script whenever the upstream Azure repo updates. |

### Security Guardrail

> **Note:** Ensure your Python script includes a "Dry Run" mode. Before any `git commit` or `policy publish` action, the script should output a summary of changes for human approval to prevent automated configuration drift in customer environments.

Would you like me to generate a starter `orchestrator.py` script that handles the local Git diffing logic?
