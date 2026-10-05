# ContextIQ — "An AI agent that understands your context before deciding what you should do."
Agentic AI hackathon project. Everyday decisions (dinner, evening plan) made by an agent that **chooses which tools to call**, gathers context, searches a real local dataset, recommends, waits for approval, then acts (`add_to_cart`).

## Install & run
```bash
cd contextiq/backend
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env        # then put your free GEMINI_API_KEY in backend/.env (create one at https://aistudio.google.com/apikey, no credit card needed)
uvicorn main:app --reload --port 8000
```
Open http://localhost:8000 (FastAPI serves the frontend; no Node build step needed).
Without an API key the app still works via the clearly-labelled rule-based fallback.

## Architecture
`frontend/index.html` → `POST /api/agent` (NDJSON stream) → `agent.py` (Google Gemini function-calling loop, model set by `GEMINI_MODEL`, default `gemini-3.5-flash-lite`) → `tools.py` → `data/foods.py`.
Each streamed event is emitted **after a real tool executes**. The agent ends by calling `submit_recommendation` / `submit_plan`; the server validates that item IDs came from `search_food` results (no invented food or prices). The cart is only touched by `POST /api/cart/add`, triggered by the user's click. If the LLM fails, `fallback.py` (deterministic scoring, same real tools) takes over and the UI says so.

## Tools
`get_activity_data`, `get_sleep_data`, `get_weather` (mock, API-swappable), `get_user_preferences`, `get_recent_meals`, `get_current_state` (hunger, time), `get_pending_tasks`, `search_food` (26-item dataset, filters), `add_to_cart` (action, user-approved).

## 2-minute demo
1. (0:00) Pitch: "Recommenders know what you like; ContextIQ asks what makes sense *right now*."
2. (0:15) Load **Active Day** → Ask ContextIQ. Narrate the live tool events; note the agent may skip weather.
3. (0:45) Show recommendation + reasons; click **Add to Cart** → cart updates.
4. (1:05) **What if?**: steps 2000, budget ₹150, hunger Medium → re-run; banner shows old → new pick.
5. (1:25) Click **Tight Budget** and **Low Activity** demos to show different picks from the same agent.
6. (1:40) **Plan My Evening** → timeline built from activity, sleep, tasks.
7. (1:55) Close with future work.

## 60-second pitch
Every day we make dozens of small decisions while our context — activity, sleep, budget, what we just ate — sits scattered across apps. Recommenders ask what you like. ContextIQ asks what makes sense for you right now. It's a true agent: given a goal it decides which tools it needs, pulls activity, sleep, preferences and meal history, searches a real food database, compares options, explains its pick from actual data, and — only after your approval — acts by adding to your cart. Change your context and it reconsiders. The same architecture plans your evening. Next: wearables, live weather, delivery APIs, calendar, voice, and learning your preferences over time.
