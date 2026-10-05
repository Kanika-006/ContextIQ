"""LLM agent: Google Gemini function-calling loop (manual). The model decides which tools to
call; every event emitted is produced by an actual tool execution."""
import os
from google import genai
from google.genai import types
import tools as T
from events import ev, summarize

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

def tool(name, desc, props=None, req=None):
    kw = {"name": name, "description": desc}
    if props:  # Gemini rejects empty OBJECT schemas, so no-argument tools omit `parameters`
        kw["parameters"] = {"type": "object", "properties": props, **({"required": req} if req else {})}
    return types.FunctionDeclaration(**kw)

READ = [
 tool("get_activity_data", "Today's step count and activity level."),
 tool("get_sleep_data", "Last night's sleep hours and quality."),
 tool("get_weather", "Current local weather."),
 tool("get_user_preferences", "Diet, budget, cuisines, dislikes."),
 tool("get_recent_meals", "Meals eaten earlier today."),
 tool("get_current_state", "Current hunger level and local time."),
 tool("get_pending_tasks", "Pending tasks with minutes+priority, available time, start time."),
]
SEARCH = tool("search_food", "Search the food database. The ONLY source of food items and prices.", {
  "max_price": {"type": "number"}, "min_protein": {"type": "number"},
  "min_calories": {"type": "number"}, "max_calories": {"type": "number"}, "max_spice": {"type": "integer", "description": "0-3"},
  "cuisine": {"type": "string"}, "query": {"type": "string"}})
SUBMIT_FOOD = tool("submit_recommendation", "Final answer. IDs must come from search_food results.", {
  "best_id": {"type": "integer"}, "alternative_ids": {"type": "array", "items": {"type": "integer"}, "description": "up to 2"},
  "reasons": {"type": "array", "items": {"type": "string"}, "description": "3-4 short reasons grounded in tool results"},
  "confidence": {"type": "string", "enum": ["High", "Medium", "Low"]}}, ["best_id", "alternative_ids", "reasons", "confidence"])
SUBMIT_PLAN = tool("submit_plan", "Final answer: a time-blocked evening plan within available time.", {
  "blocks": {"type": "array", "items": {"type": "object", "properties": {"start": {"type": "string", "description": "HH:MM"},
   "end": {"type": "string", "description": "HH:MM"}, "activity": {"type": "string"}, "reason": {"type": "string"}},
   "required": ["start", "end", "activity", "reason"]}}, "summary": {"type": "string"}}, ["blocks", "summary"])

SYSTEM = {
 "food": "You are ContextIQ, an agent deciding what the user should order for dinner. Decide which context tools are relevant "
         "(skip irrelevant ones, e.g. weather for an indoor meal). Gather context, then call search_food with filters derived from it "
         "(budget as max_price, calories for hunger, protein for activity; the user's diet preference from get_user_preferences is enforced automatically by search_food, so do not filter diet yourself), compare candidates, and finish with submit_recommendation. "
         "A bigger budget does not mean a pricier meal: choose a sensible single-person dinner, and do not recommend items marked \"serves N\" or group combos. Never invent items or prices. Reasons must cite actual tool results. Do not reveal hidden reasoning.",
 "evening": "You are ContextIQ, an agent planning the user's evening. Use tools to gather relevant context (activity, sleep, tasks), "
            "then finish with submit_plan: contiguous time blocks starting at the start time, ending within available time, "
            "including dinner (30 min), breaks, and every task as time allows. Shorten work blocks if sleep was poor; add a walk if steps are low.",
}
TOOLSETS = {"food": READ + [SEARCH, SUBMIT_FOOD], "evening": READ + [SUBMIT_PLAN]}

def run(mode, goal, ctx):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    cfg = types.GenerateContentConfig(
        system_instruction=SYSTEM[mode], max_output_tokens=2048,
        tools=[types.Tool(function_declarations=TOOLSETS[mode])],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True))  # we run the loop ourselves
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=goal)])]
    seen, compared = {}, 0
    yield ev(None, "Understanding request", goal)
    for _ in range(10):
        r = client.models.generate_content(model=MODEL, contents=contents, config=cfg)
        if not r.candidates or not r.candidates[0].content:
            raise RuntimeError("Gemini returned no content")
        contents.append(r.candidates[0].content)  # keep the model turn verbatim (preserves thought signatures)
        calls = r.function_calls or []
        if not calls: raise RuntimeError("Agent ended without submitting an answer")
        parts, final = [], None
        for c in calls:
            a = dict(c.args or {})
            try:
                if c.name == "submit_recommendation":
                    ids = [int(a["best_id"])] + [int(i) for i in list(a.get("alternative_ids", []))[:2]]
                    bad = [i for i in ids if i not in seen]
                    if bad: raise ValueError(f"ids {bad} were not returned by search_food")
                    final = {"type": "result", "kind": "food", "source": "agent", "compared": compared,
                             "best": seen[ids[0]], "alternatives": [seen[i] for i in ids[1:]],
                             "reasons": list(a["reasons"]), "confidence": a["confidence"]}
                    out = {"ok": True}
                elif c.name == "submit_plan":
                    final = {"type": "result", "kind": "evening", "source": "agent",
                             "blocks": [dict(b) for b in a["blocks"]], "summary": a["summary"]}
                    out = {"ok": True}
                elif c.name in T.READ_TOOLS:
                    out = T.READ_TOOLS[c.name](ctx, **a)
                    if c.name == "search_food":
                        seen.update({f["id"]: f for f in out}); compared = len(seen)
                    yield ev(c.name, None, summarize(c.name, out), a)
                else: raise ValueError("unknown tool")
                parts.append(types.Part.from_function_response(name=c.name, response={"result": out}))
            except Exception as e:  # invalid tool call -> tell the model, let it recover
                parts.append(types.Part.from_function_response(name=c.name, response={"error": str(e)}))
        if final:
            yield ev(None, "Selected recommendation" if mode == "food" else "Plan created", "ready")
            yield final; return
        contents.append(types.Content(role="user", parts=parts))
    raise RuntimeError("Agent exceeded step limit")
