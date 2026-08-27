# AI-Agent-Restaurant

A modular **Restaurant AI Agent** built with Python. The project provides a Gradio chat interface where customers can ask about the menu, reservations, orders, invoices, registration, and complaints. The agent uses an OpenAI-compatible client connected to Groq for model responses, Supabase for conversation memory and handoff state, and function calling to access the restaurant business operations.

## Project Objective

The goal is to provide a practical customer-service assistant that can understand a customer request, use the correct restaurant function when live data or an action is required, and return a concise response in polite Egyptian Arabic. The agent is designed to avoid hallucinating prices, availability, identifiers, invoice totals, or operation results.

This project is organized as a **modular monolith**: the application runs as one service, while each responsibility is separated into a clear module. The original team-owned business logic remains under `tasks/team_code/` and is accessed through wrappers without changing its classes or terminology.

## Main Capabilities

| Capability | Description |
| --- | --- |
| Menu assistance | Display the full menu, search for items, and filter by category. |
| Table service | Check availability, list available tables, create reservations, and cancel reservations. |
| Orders and invoices | Create orders, add or remove items, check order status, and calculate invoices. |
| Customer service | Register customers, record complaints, and retrieve customer complaint history. |
| Conversation memory | Save user and assistant messages in Supabase and load recent context for each chat. |
| Human handoff | Stop the AI and notify the customer when a human employee is required. |
| Chat interface | Provide a responsive Gradio interface with right-to-left support for Arabic text. |

## Architecture

```
project_finals/
├── agentic_system/
│   ├── agent/
│   │   ├── ai_agent.py          # Main orchestration and tool loop
│   │   ├── prompts.py           # System and handoff prompts
│   │   └── handoff.py           # Response-quality and escalation logic
│   │
│   ├── integrations/
│   │   ├── db_config.py         # Supabase client configuration
│   │   └── llm_client.py        # Groq/OpenAI-compatible client
│   │
│   ├── memory/
│   │   └── supabase_memory.py   # Chat history and session state
│   │
│   ├── tools/
│   │   ├── tool_registry.py     # Tool schemas and function mapping
│   │   ├── menu_tools.py        # Menu, table, and reservation wrappers
│   │   ├── orders_tools.py      # Order and invoice wrappers
│   │   ├── customer_tools.py    # Customer and complaint wrappers
│   │   └── reservation_tools.py
│   │
│   └── ui/
│       └── gradio_app.py        # Gradio layout, callback, and CSS
│
├── tasks/team_code/             # Team-owned business logic; unchanged
├── assets/                      # Project assets
├── main.py                      # Application entry point
├── pyproject.toml               # Project metadata and dependencies
├── requirements.txt             # Readable dependency list
├── uv.lock                      # Locked dependency versions
├── .python-version              # Project Python version
├── .env.example                 # Safe environment-variable template
└── .gitignore                   # Files excluded from Git
```

### Responsibilities

| Module | Responsibility |
| --- | --- |
| `agent/ai_agent.py` | Loads context, calls the model, executes tools, applies handoff rules, and saves the final turn. |
| `agent/prompts.py` | Defines the English system instructions and the handoff-classifier instructions. |
| `agent/handoff.py` | Checks whether the current turn requires escalation. |
| `integrations/` | Creates the Groq/OpenAI-compatible client and the Supabase client. |
| `memory/` | Reads and writes chat messages and session state. |
| `tools/tool_registry.py` | Exposes the exact function schemas sent to the model and maps names to Python functions. |
| `tools/` wrappers | Connects the agent to the Team Code without changing the Team Code itself. |
| `ui/gradio_app.py` | Receives customer messages and displays the conversation. |

## Request Flow

```
Customer message
      ↓
Gradio interface
      ↓
Load handoff state and recent history from Supabase
      ↓
Main LLM call with registered function schemas
      ↓
Tool call when live data or an action is required
      ↓
Tool registry → wrapper → Team Code
      ↓
Tool result returned to the LLM
      ↓
Final Egyptian Arabic response
      ↓
Save user and assistant messages in Supabase
```

The model does not directly modify the Team Code. It requests a registered function, and the application executes the corresponding wrapper. The returned result is then provided to the model so it can answer using real data.

## Registered Tools

The application currently registers 15 tools:

| Area | Registered functions |
| --- | --- |
| Menu | `get_menu`, `search_menu_item`, `get_menu_by_category` |
| Tables and reservations | `check_table_availability`, `get_available_tables`, `make_reservation`, `cancel_reservation` |
| Orders and invoices | `create_order`, `add_item_to_order`, `remove_item_from_order`, `get_order_status`, `calculate_invoice` |
| Customers and complaints | `register_customer`, `log_complaint`, `get_customer_history` |

The definitions and parameter types are centralized in `tool_registry.py`. The bracketed names documented in the prompt are only descriptions; actual calls use the exact names and schemas registered by the application.

## Conversation Memory and Handoff

Supabase is used for the assistant's persistent conversation state. The application uses two tables:

| Table | Stored data |
| --- | --- |
| `n8n_chat_histories` | User and assistant messages stored as JSON under the chat session ID. |
| `restaurant_chat_sessions` | Handoff status, escalation reason, failure counter, and update time. |

The current agent configuration loads the latest **10 messages** for context through `HISTORY_LIMIT` in `ai_agent.py`. The application stores only the customer-facing user and assistant messages, not raw tool payloads or the system prompt.

Human handoff is activated when the customer clearly requests an employee, shows strong anger, or submits a serious complaint. The quality classifier also counts consecutive unsuitable responses. After three consecutive failures, the AI is stopped for that chat and the customer receives a message that a human employee will follow up.

## Important Data Note

Supabase stores conversation history and handoff state only. The current menu, reservation, customer, complaint, order, and invoice objects are managed by the local Team Code and wrapper instances. Therefore, some business data is process-local and may reset when the application restarts. This is an intentional separation for the current project scope.

## Requirements

The project uses Python `3.13`, as specified by `.python-version`. It requires a Groq API key and a Supabase project containing the two tables described above.

The direct dependencies currently resolved in `uv.lock` are:

| Package | Locked version | Purpose |
| --- | --- | --- |
| `gradio` | `6.26.0` | Web-based chat interface. |
| `openai` | `3.3.1` | OpenAI-compatible client interface used with Groq. |
| `groq` | `1.7.0` | Groq Python package available to the project environment. |
| `supabase` | `2.31.0` | Supabase database client. |
| `python-dotenv` | `1.2.3` | Loads local variables from `.env`. |
| `pandas` | `3.0.5` | Used by the Team Code menu implementation. |

The project metadata and dependency declarations are stored in `pyproject.toml`. The exact resolved versions, including transitive dependencies, are stored in `uv.lock`. The pinned `requirements.txt` is kept as a readable and portable dependency list for environments or tools that expect that file. It does not replace `pyproject.toml` or `uv.lock` in the recommended UV workflow.

`json`, `os`, `datetime`, `logging`, and `uuid` are Python standard-library modules, so they are not installed as third-party packages and should not be added to `requirements.txt`.

## Why UV Is Used

`uv` is a Python project and package manager from Astral. It was used instead of managing packages manually with separate `pip` and virtual-environment commands because it combines dependency installation, virtual-environment management, command execution, and lock-file handling in one workflow.[1]

For this project, UV provides three practical benefits:

1. It creates and manages the isolated `.venv` environment, preventing project packages from mixing with global Python packages.

1. It reads `pyproject.toml` and synchronizes the environment with the exact versions recorded in `uv.lock`.

1. It allows commands to run inside the project environment through `uv run`, without requiring manual activation of `.venv`.[2]

This makes setup easier for beginners and improves reproducibility when the project is installed on another machine.

## Installation and Setup

### 1. Install UV

On Windows PowerShell, use the official installer:

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then restart PowerShell and verify the installation:

```
uv --version
```

### 2. Clone the repository

```
git clone https://github.com/fareselmetwaly/AI-Agent-Restaurant.git
cd AI-Agent-Restaurant
```

### 3. Create the project environment

```
uv sync
```

This reads `pyproject.toml`, uses the versions recorded in `uv.lock`, and creates or updates the local `.venv` environment. The `.venv` directory is intentionally excluded from Git.

For this project, do not install the same dependencies twice with separate `pip` commands after running `uv sync`. Use `requirements.txt` only when another tool specifically requires a requirements file. If that alternative is needed, the pinned list can be installed with:

```
uv add -r requirements.txt
```

The normal and recommended command remains `uv sync`, because it keeps the environment synchronized with the project metadata and lock file.

### 4. Create the local environment file

```
Copy-Item .env.example .env
```

Open `.env` and provide the real values locally:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-server-only-supabase-secret
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=your-groq-model
GROQ_HANDOFF_MODEL=your-handoff-model
PORT=7860
```

The Supabase service-role key and Groq API key are server-side secrets. They must never be placed in the README, committed to Git, or exposed in frontend code.

### 5. Prepare the Supabase tables

Create the following application tables in the Supabase project before running the agent:

```sql
create table public.n8n_chat_histories (
    id serial primary key,
    session_id varchar(255 ) not null,
    message jsonb not null
);

create table public.restaurant_chat_sessions (
    chat_id text primary key,
    human_handoff boolean not null default false,
    escalation_reason text,
    failed_attempts integer not null default 0,
    updated_at timestamptz not null default now()
);
```

The application uses the Supabase service-role key on the backend to read and write these tables. No menu or order data is stored in Supabase by this application.

## Running the Application

Run the application from the repository root so Python can resolve the `agentic_system` package:

```
uv run python main.py
```

Open the interface at:

```
http://127.0.0.1:7860
```

## Basic Verification

Check that the main Python modules compile successfully:

```
uv run python -m py_compile `
  agentic_system/agent/ai_agent.py `
  agentic_system/agent/prompts.py `
  agentic_system/agent/handoff.py `
  agentic_system/integrations/llm_client.py `
  agentic_system/memory/supabase_memory.py `
  agentic_system/ui/gradio_app.py `
  main.py
```

Then start the application:

```
uv run python main.py
```

A suitable manual conversation test is:

```
عاوز اعرف صنف Margrita
طيب عاوز اطلبه
```

The second message should use the recent conversation context and refer to the previously identified menu item instead of asking for the item name again.

## Security and Git Practices

The repository includes `.gitignore` rules for `.env`, `.venv`, Python caches, logs, and generated local files. Before every commit, review the staged files:

```
git status --short
git diff --cached
```

Only `.env.example` should be committed. If a real secret is ever committed, it must be revoked and replaced immediately; deleting the local file alone does not remove it from Git history.

## References

1. [uv official documentation](https://docs.astral.sh/uv/ )
2. [uv: Working on projects](https://docs.astral.sh/uv/guides/projects/ )
3. [uv: Installation](https://docs.astral.sh/uv/getting-started/installation/ )
