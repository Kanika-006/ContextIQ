"""Deterministic rule-based fallback. Clearly separate from the LLM agent: used only
when the LLM is unavailable. It still calls the same real tools and reports it as 'fallback'."""
import tools as T
from events import ev, summarize

def _t(s): h, m = map(int, s.split(":")); return h * 60 + m
def _s(m): return f"{m // 60 % 24:02d}:{m % 60:02d}"

def run_food(ctx):
    yield ev(None, "Rule-based fallback engaged (LLM not used)", "deterministic scoring")
    got = {}
    for name in ["get_activity_data", "get_user_preferences", "get_recent_meals", "get_current_state"]:
        out = T.READ_TOOLS[name](ctx); got[name] = out
        yield ev(name, None, summarize(name, out))
    act, pref, meals, st = (got[k] for k in got)
    args = {"max_price": pref["budget"], "max_spice": 2}  # diet is enforced inside search_food
    items = T.search_food(ctx, **args)
    yield ev("search_food", None, summarize("search_food", items), args)
    if not items:
        yield {"type": "error", "message": "No food matches this budget/diet. Try raising the budget."}; return
    target = {"High": 700, "Medium": 520, "Low": 350}[st["hunger"]] - (120 if act["activity_level"] == "low" else 0)
    pw = {"high": 1.5, "moderate": 1.4, "low": 0.4}[act["activity_level"]]
    toks = {w for m in meals for w in m["meal"].lower().split()}
    scored = []
    for f in items:
        s = 2 * (1 - min(abs(f["calories"] - target) / target, 1)) + pw * min(f["protein"], 40) / 30
        s += 0.3 * (f["price"] <= 0.9 * pref["budget"])
        if toks & set(f["name"].lower().replace("+", " ").split()): s -= 0.5
        scored.append((s, f))
    scored.sort(key=lambda x: -x[0])
    best, alts = scored[0][1], [f for _, f in scored[1:3]]
    reasons = [f"{act['steps']} steps today ({act['activity_level']} activity); {best['protein']}g protein suits that.",
               f"Hunger is {st['hunger'].lower()}; ~{best['calories']} kcal is close to a ~{target} kcal target.",
               f"₹{best['price']} fits your ₹{pref['budget']} budget.",
               "Different from your recent meals." if not toks & set(best["name"].lower().split()) else "Similar to a recent meal, but best overall fit."]
    if pref["diet"] != "any": reasons.insert(2, f"Matches your {pref['diet']} preference.")
    conf = "High" if len(scored) > 1 and scored[0][0] - scored[1][0] > 0.3 else "Medium"
    yield ev(None, "Selected recommendation", best["name"])
    yield {"type": "result", "kind": "food", "source": "fallback", "compared": len(items),
           "best": best, "reasons": reasons, "confidence": conf, "alternatives": alts}

def run_evening(ctx):
    yield ev(None, "Rule-based fallback engaged (LLM not used)", "deterministic planner")
    got = {}
    for name in ["get_activity_data", "get_sleep_data", "get_pending_tasks"]:
        got[name] = T.READ_TOOLS[name](ctx); yield ev(name, None, summarize(name, got[name]))
    act, sl, tk = got.values()
    t, end = _t(tk["start_time"]), _t(tk["start_time"]) + tk["available_minutes"]
    blocks = []
    def add(dur, what, why):
        nonlocal t
        if t + dur <= end: blocks.append({"start": _s(t), "end": _s(t + dur), "activity": what, "reason": why}); t += dur; return True
    if act["activity_level"] == "low": add(20, "Walk", f"Only {act['steps']} steps so far.")
    add(30, "Dinner", "Fuel before focused work.")
    cap = 40 if sl["sleep_quality"] == "poor" else 60
    for task in sorted(tk["tasks"], key=lambda x: x["priority"]):
        if t >= end: break
        if blocks[-1]["activity"] != "Dinner" and blocks[-1]["activity"] != "Break": add(10, "Break", "Short reset.")
        add(min(task["minutes"], cap), task["title"], f"Priority {task['priority']}" + (" (shortened: poor sleep)" if sl["sleep_quality"] == "poor" else ""))
    yield ev(None, "Plan created", f"{len(blocks)} blocks")
    yield {"type": "result", "kind": "evening", "source": "fallback", "blocks": blocks, "summary": "Rule-based plan."}
