# CURT Inventory Assistant

An inventory assistant for the Cairo University Racing Team (CURT) Formula Student team. It allows team members to query parts, check quantities, verify storage locations, list categories, and flag low-stock shortages.

The project is built in two phases:
- **Phase 1**: Rule-based natural language parser without an LLM.
- **Phase 2**: LLM-powered assistant using Google Gemini with function calling, conversation context memory, and a FastAPI backend.
- **Frontend**: A unified Streamlit application with tabs allowing instant switching between Phase 1 and Phase 2, alongside a live inventory table.

---

## Tech Stack & Architecture

- **Database**: SQLite (`core/curt_inventory.db`)
- **Backend API**: FastAPI + Uvicorn (`phase2/api.py`)
- **LLM & Tool Calling**: Google Gemini (`google-genai` SDK) via `phase2/llm_service.py`
- **Frontend**: Streamlit (`app.py`)
- **Environment**: Python 3.10+, `python-dotenv`

### System Flow (Phase 2):
```
User (Streamlit UI)
      ↓ HTTP POST
FastAPI (/chat)
      ↓
LLM Service (Gemini API)
      ↓ Function Call Request
Dispatcher / Tools (tools.py)
      ↓
Data Access Layer (data_access.py)
      ↓
SQLite Database (curt_inventory.db)
```

---

## Local Setup & How to Run

### 1. Clone & Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file inside `phase2/` (or copy from `.env.example`):
```powershell
cp .env.example phase2/.env
```
Add your Gemini API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key
```

### 3. Database Setup (Already Seeded)
The database is located at `core/curt_inventory.db`. If you need to re-seed from scratch using `core/schema.sql`:
```powershell
sqlite3 core/curt_inventory.db < core/schema.sql
```

### 4. Run the Application
Open two terminal windows:

- **Terminal 1: Start FastAPI Backend**
  ```powershell
  cd phase2
  uvicorn api:app --reload
  ```
  FastAPI runs on `http://127.0.0.1:8000`. You can explore the API docs at `http://127.0.0.1:8000/docs`.

- **Terminal 2: Start Streamlit Frontend**
  ```powershell
  streamlit run app.py
  ```
  Opens the app in your browser (usually `http://localhost:8501`) with tabs for Phase 1 and Phase 2.

---

## API Endpoints

- `POST /chat`: Accepts JSON `{"session_id": "...", "message": "..."}`, processes the question through Gemini with tool calling, and returns `{"reply": "..."}`.
- `GET /inventory`: Returns all parts from the database as JSON objects `[{"id": 1, "name": "...", "quantity": 8, "category": "...", "location": "..."}]`.

---

## Task 1 — Database & Data Access

I started by designing a SQLite database called `curt_inventory.db` under `core/`.

The main table schema is:
```sql
CREATE TABLE IF NOT EXISTS parts (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    quantity INTEGER NOT NULL CHECK (quantity >= 0) DEFAULT 0,
    category TEXT NOT NULL,
    location TEXT NOT NULL
);
```

I deliberately made `name UNIQUE` because each inventory item needs an unambiguous identity, especially when the LLM later requests a specific item via tool calling.

I seeded the database with realistic Formula Student parts across mechanical, electrical, and powertrain subsystems:
`Brake Disc`, `Brake Pad Set`, `Wheel Bearing`, `Tie Rod End`, `Steering Rack`, `Control Arm`, `CV Joint`, `Drive Shaft`, `Spark Plug`, `Oil Filter`.

I created a dedicated data-access layer (`data_access.py`) responsible for all SQLite operations: didn't use all of them 
- `get_part(name)`
- `list_by_category(category)`
- `get_quantity_of_part(name)`
- `get_location_of_part(name)`
- `check_stock(item_name)`
- `flag_shortage(item_name)`
- `get_all_parts()`

I intentionally kept the data-access layer separate from the AI logic so the database operations could be reused cleanly across both phases.

---

## Task 2 — Phase 1 (Rule-Based Assistant)

Before touching an LLM, I built a rule-based assistant in `phase1/`. The goal was to understand the underlying parsing logic and data flow without relying on AI.

I defined keyword groups to detect user intent:
- `LOCATION_KEYWORDS = {"where", "location", "place", "shelf", "rack", "find", "stored"}`
- `QUANTITY_KEYWORDS = {"how many", "quantity", "count", "stock", "left", "available", "units"}`
- `CATEGORY_KEYWORDS = {"list", "show", "items in", "parts in", "category"}`

The parser matched items and categories against predefined lists and determined whether the user was asking about quantity, location, or listing a category.

Architecture:
```
User → Streamlit → Rule-based parser → Data access layer → SQLite
```

Building this first helped me clearly see what an LLM actually replaces: it replaces the rigid parsing layer, while the database operations remain standard code.

---

## Task 3 — Phase 2 (LLM Assistant with Function Calling)

For Phase 2, I introduced Google Gemini via the `google-genai` SDK and built a FastAPI backend.

### Controlled Tool Calling
Gemini never gets direct access to SQLite or raw SQL execution. Instead, I exposed three controlled tool definitions:
- `check_stock(item_name)`: Checks the current quantity and storage location.
- `list_by_category(category)`: Retrieves all parts in a category.
- `flag_shortage(item_name)`: Checks if quantity is below threshold (10 units) and logs a shortage alert.

When Gemini receives a prompt like *"Do we have enough brake discs?"*, it decides to call `check_stock` or `flag_shortage`. My backend intercepts the tool call, executes the Python function in `data_access.py`, queries SQLite, and sends the structured result back to Gemini so it can formulate the final natural language answer.

I implemented a while loop in `llm_service.py` to handle multi-step tool calls (for example: check stock → notice low stock → flag shortage → final response).

I considered exposing `get_part()` directly as a tool, but kept it as an internal helper function so as not to clutter the model with redundant low-level tools. I also considered MCP, but decided against adding it for now to avoid unnecessary complexity.

### Multi-Turn Conversation Memory
To persist context across HTTP requests, I maintained an in-memory dictionary:
```python
SESSION_STORE: dict[str, str] = {}
```
This maps `session_id → previous_interaction_id`. When the user asks a follow-up:
```
User: Do we have enough brake discs?
AI: We have 8 Brake Discs in stock, located at Shelf A1. This is below our threshold of 10 units.

User: Where are they?
AI: They are located at Shelf A1.
```
Gemini uses `previous_interaction_id` to recognize that *"they"* refers to Brake Discs from the previous turn. In-memory storage was used as allowed by the assignment guidelines.

---

## Task 4 — Streamlit Frontend

I built a Streamlit frontend in `app.py` that includes:
- A chat-style input and message bubble display with conversation history.
- A live inventory sidebar that calls `GET /inventory` on FastAPI and displays a real-time table with a refresh button.
- A tab switcher (`Phase 1` and `Phase 2`) at the top of the page so the reviewer can switch between the rule-based parser and the LLM assistant without restarting the app.
- Both tabs share a consistent, clean UI layout matching the Formula Student theme.

---

## Task 5 — Edge Case Handling

### 1. Missing Items
- **Phase 1**: If an item name does not match any known string in the hardcoded list, the parser outputs that the part was not recognized.
- **Phase 2**: If the user asks about an item that does not exist in the database (e.g., *"How many turbochargers do we have?"*), Gemini calls `check_stock("Turbocharger")`. The data-access layer finds no matching record and returns `{"error": "Item 'Turbocharger' was not found."}`. Gemini interprets this error and politely informs the user that the item does not exist in the inventory. The model does not hallucinate quantities or invent fake items.

### 2. Typos and Partial Names
- **Phase 1**: Relies on direct substring and keyword matching. If the user makes a typo (e.g., *"brak disk"* instead of *"brake disc"*), Phase 1 fails to identify the part because it lacks spelling tolerance.
- **Phase 2**: Because Gemini understands natural language semantically, it can map minor typographical errors or variations (such as plural forms *"brake discs"* or lowercasing *"brake disc"*) to the exact item name expected by the tool (`"Brake Disc"`). However, this is semantic interpretation rather than guaranteed fuzzy string matching. If an input is heavily mangled or genuinely ambiguous, the model does not guess wildly; if an incorrect name reaches `data_access.py`, the database safely returns a "not found" response.

### 3. Ambiguous Questions
- **Example**: *"How many do we have?"* with no item mentioned.
- **Phase 1**: The parser detects the quantity keyword (`"how many"`), but fails to find any item or category keyword. It defaults to asking the user to specify a part.
- **Phase 2**: Because Gemini receives the question without an item name and without any prior context (if starting a new session), it realizes it lacks the required parameter for `check_stock`. Instead of calling a tool with a made-up item, Gemini asks the user for clarification: *"Which part would you like to check the quantity for?"*. If it is a follow-up question in an ongoing session, it uses the conversation memory to resolve the pronoun.

---

## Task 6 — Reflection

### Why I Made These Architectural Decisions:
1. **Starting with Phase 1 first**: Building the rule-based parser before touching an LLM was valuable. It forced me to map out how natural language maps to database queries, and showed me exactly where rule-based parsing breaks down and where an LLM shines.
2. **Dedicated Data Access Layer**: Keeping `data_access.py` strictly focused on SQLite and completely decoupled from both the parser and Gemini allowed me to reuse the exact same database and queries in both phases.
3. **FastAPI Backend**: Rather than putting LLM calls and database queries directly inside the Streamlit script, putting them behind FastAPI gave the project a clean client-server separation. Streamlit only acts as a presentation client.
4. **Controlled Function Calling vs. Raw SQL**: Allowing an LLM to generate raw SQL queries against a database is risky and unpredictable. By exposing three purpose-built tools (`check_stock`, `list_by_category`, `flag_shortage`), the LLM only chooses *what* business operation it wants; my code controls *how* the database is accessed.
5. **In-Memory Session Storage**: An in-memory dictionary mapping `session_id` to Gemini interaction IDs was the simplest, cleanest solution that satisfied the requirements without introducing database migration complexity for chat history.
6. **Avoiding MCP for Now**: I considered using an MCP server for tool execution, but decided against it to keep the codebase easy to run, review, and debug without external process managers.
7. **Live Sidebar Table**: Displaying the SQLite inventory table live in the sidebar makes it immediately obvious during testing and demonstration that the assistant is reading and reacting to real database state.

### What I Would Improve With More Time:
- **Persistent Session Storage**: Replace the in-memory dictionary with Redis or a SQLite `conversations` table so chat history survives server restarts.
- **Database-Level Fuzzy Matching**: Add phonetic or Levenshtein distance matching in SQLite/Python (e.g., using `fuzzywuzzy` or SQLite's `LIKE`) so the backend itself can handle minor typos even if a tool is called with a slightly misspelled string.
- **Automated Shortage Alerts**: Connect `flag_shortage` to an actual notification channel (like a Slack/Discord webhook or email) so team leads get notified when parts fall below the threshold.
- **Inventory Modification Tools**: Add tools to update stock, restock parts, or log part checkouts with audit trails.
- **API Authentication & Rate Limiting**: Add API key or JWT authentication to `/chat` and `/inventory` to protect team data.
- **Automated Test Suite**: Write `pytest` test suites covering the parser keyword combinations, FastAPI endpoints, tool dispatcher responses, and database error states.
