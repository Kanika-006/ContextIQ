# ContextIQ

> **AI that understands your context before making a decision.**

ContextIQ is an **agentic AI assistant for context-aware everyday decision-making**.

Instead of simply asking an LLM for a recommendation, ContextIQ uses an AI agent that can gather relevant user context through tools, search available options, apply constraints such as dietary preference and budget, and provide a recommendation for the user to approve.

The current prototype demonstrates this workflow through **context-aware food recommendations**, with the architecture designed to be extended to other everyday decisions.

---

## Problem

Everyday decisions are often made using fragmented information.

For something as simple as deciding what to eat, a person may need to consider their current activity, sleep, hunger, recent meals, dietary preference, and available budget. Conventional recommendation systems often focus primarily on static preferences or past behavior instead of bringing relevant current context together.

This can result in recommendations that are technically suitable but not necessarily appropriate for the user's situation at that moment.

---

## Solution

ContextIQ introduces an **agentic decision-making workflow**.

When a user asks something such as:

> **"What should I order for dinner tonight?"**

the ContextIQ agent can:

1. Understand the user's goal.
2. Determine which available context is relevant.
3. Call tools to retrieve that information.
4. Gather context such as activity, sleep, hunger, dietary preference, recent meals, and budget.
5. Search the available food options.
6. Apply dietary and budget constraints.
7. Reason over the collected information.
8. Generate a recommendation.
9. Validate the recommendation against available options.
10. Ask the user for approval before performing an action such as adding the item to the cart.

This turns a simple recommendation request into a **multi-step agentic workflow**.

---

## Why ContextIQ?

Traditional recommendation:

```text
User Preference
      ↓
Recommendation
```

ContextIQ:

```text
User Goal
    ↓
AI Agent
    ↓
Determine Relevant Context
    ↓
Use Tools
    ↓
Gather Information
    ↓
Search Available Options
    ↓
Apply Constraints
    ↓
Reason Over Context
    ↓
Recommendation
    ↓
User Approval
    ↓
Action
```

The key idea is simple:

> **Don't recommend only what the user likes. Understand the situation before recommending what they should choose.**

---

# Key Features

## AI Agent with Tool Calling

ContextIQ uses the Google Gemini API with function/tool calling. The agent can determine which tools are useful for the user's request and use their results during the decision-making process.

## Context-Aware Decision Making

The system can work with multiple pieces of user context, including:

- Activity
- Sleep
- Hunger level
- Dietary preference
- Recent meals
- Budget

These inputs provide the agent with a broader picture of the user's current situation.

## Dietary Preference

Users can select:

- **Vegetarian**
- **Non-vegetarian**
- **No preference**

The selected dietary preference is respected during the food-search and recommendation workflow.

## Budget-Aware Recommendations

Users can select a budget between:

```text
₹100 → ₹2,000
```

The selected budget is passed into the food-search workflow so that recommendations remain within the user's spending constraint.

## Context-Aware Food Search

The agent does not simply invent a food recommendation.

It searches the available structured food dataset and uses the returned options when generating its recommendation.

## Recommendation Validation

The system validates recommendations against the available search results, helping prevent the agent from recommending an unavailable item.

## What-If Scenarios

Users can change contextual inputs and explore how the recommendation changes under a different scenario.

For example:

```text
Current Scenario
8,700 steps
₹300 budget
Vegetarian
      ↓
Recommendation

        ↓ Change Context

Different Scenario
Higher activity
Different budget
Same dietary preference
      ↓
New Recommendation
```

## User Approval Before Action

The recommendation is presented to the user before the action is performed.

After approval, the prototype can simulate adding the selected item to a cart.

---

# Example

Suppose a user asks:

> **"What should I order for dinner tonight?"**

ContextIQ may have access to:

| Context | Example |
|---|---|
| Activity | 8,700 steps |
| Sleep | 7.4 hours |
| Hunger | High |
| Dietary preference | Vegetarian |
| Budget | ₹300 |
| Recent meals | Available to the agent |

The agent gathers the relevant information, searches valid food options, applies the user's constraints, reasons over the available context, and produces a recommendation.

The user can then:

- Accept the recommendation
- Add it to the simulated cart
- Change the context using What-If controls
- Explore a different recommendation

---

# Agent Architecture

ContextIQ uses a **single agent with multiple tools** rather than a simple prompt-and-response system.

```text
                    User Goal
                       │
                       ▼
                ┌─────────────┐
                │ ContextIQ   │
                │    Agent    │
                └──────┬──────┘
                       │
                       ▼
             Determine Required Context
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      Activity       Sleep      Preferences
          │            │            │
          └────────────┼────────────┘
                       │
                       ▼
                 Recent Meals
                       │
                       ▼
                 Gather Context
                       │
                       ▼
                 Search Food
                       │
                       ▼
              Apply Diet + Budget
                   Constraints
                       │
                       ▼
                Agent Reasoning
                       │
                       ▼
                Recommendation
                       │
                       ▼
                 User Approval
                       │
                       ▼
                 Cart Action
```

---

# Tool-Based Workflow

The prototype includes tools for working with different parts of the user's context and decision process.

### Context Tools

- Activity data
- Sleep data
- User preferences
- Recent meals

### Decision Tools

- Food search
- Recommendation submission/validation
- Plan/action submission

### Action

- Simulated add-to-cart functionality

The agent can call the appropriate tools as part of its multi-step workflow.

---

# Dietary and Budget Logic

ContextIQ supports three dietary modes.

### Vegetarian

Only vegetarian food options are considered.

### Non-vegetarian

Non-vegetarian options are allowed according to the selected preference.

### No Preference

Both vegetarian and non-vegetarian options can be considered.

The food-search workflow also uses the user's selected budget when filtering available options.

This ensures that the recommendation is constrained by the user's explicit requirements rather than being generated independently of them.

---

# What-If Analysis

ContextIQ includes a What-If workflow that allows users to modify their scenario and see how the decision changes.

For example:

```text
Scenario A
──────────
Steps: 8,700
Budget: ₹300
Diet: Vegetarian

        ↓

Recommendation A


        ↓ Modify Context


Scenario B
──────────
Steps: Higher
Budget: ₹1,000
Diet: Vegetarian

        ↓

Recommendation B
```

This demonstrates the advantage of a context-driven decision system: **changing the situation can change the decision.**

---

# Technology Stack

## Frontend

- HTML
- CSS
- JavaScript

## Backend

- Python
- FastAPI
- Uvicorn

## AI

- Google Gemini API
- Gemini function/tool calling

## Data

- Structured food dataset
- User context data

## Development

- Python virtual environment
- Git
- GitHub

---

# Project Structure

```text
ContextIQ/
│
├── backend/
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   └── foods.py
│   │
│   ├── agent.py
│   ├── events.py
│   ├── fallback.py
│   ├── main.py
│   ├── tools.py
│   └── requirements.txt
│
├── frontend/
│   └── index.html
│
├── .env.example
├── .gitignore
└── README.md
```

---

# Getting Started

## Prerequisites

Make sure you have:

- Python 3.10+
- Git
- A Google Gemini API key

---

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/ContextIQ.git
cd ContextIQ
```

---

## 2. Create a Virtual Environment

Move into the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

---

## 3. Activate the Virtual Environment

### Windows PowerShell

```powershell
.venv\Scripts\activate
```

---

## 4. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## 5. Configure the Gemini API

Create a `.env` file inside the `backend` directory.

Add:

```text
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_gemini_model
```

Replace the values with your own Gemini configuration.
---

## 6. Run the Application

From the `backend` directory:

```powershell
uvicorn main:app --reload --port 8000
```

Open the application in your browser:

```text
http://localhost:8000
```

---

# Security

API credentials are stored through environment variables and are excluded from version control using `.gitignore`.

The repository contains `.env.example` as a template, but **never contains the actual Gemini API key**.

---

# Current Prototype Scope

The current implementation demonstrates the agentic workflow through food decision-making.

It includes:

- Context collection
- Gemini-powered agent
- Function/tool calling
- Activity context
- Sleep context
- Hunger context
- Dietary preferences
- Recent meal context
- Budget constraints
- Food search
- Recommendation validation
- What-If scenarios
- User approval
- Simulated cart action

The food dataset is currently local and structured rather than connected to a live food-delivery platform.

---

# Future Scope

The current prototype uses a structured local dataset and simulated actions. Future versions can connect ContextIQ with real-world services and APIs to make its decisions more useful and actionable.

- Integrate wearable/fitness, calendar, weather, food-delivery, and shopping APIs for live context and data.
- Enable approved real-world actions such as adding items to carts, creating calendar events, or planning activities.
- Extend the same agentic workflow beyond food to shopping, travel, productivity, and other everyday decisions.

The long-term goal is to build a context-aware decision assistant that can understand a user's situation, use information from connected services, and take useful actions with the user's approval.

---

# Hackathon Track

**Agentic AI**

ContextIQ is designed around an agentic workflow in which an AI agent can:

- Interpret a user's goal
- Determine what information it needs
- Use tools to retrieve that information
- Search constrained options
- Reason over the collected context
- Generate and validate a recommendation
- Wait for user approval
- Perform an approved action

This makes the project more than a simple LLM chatbot or static recommendation system.

---

# Project Status

**Working Prototype**

The current prototype successfully demonstrates the core ContextIQ workflow from user request → context gathering → tool calls → constrained search → AI reasoning → recommendation → user approval → action.

---

#  Developer

ContextIQ was designed and developed independently as an **Agentic AI hackathon project** focused on context-aware everyday decision-making.

---