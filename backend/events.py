LABELS = {"get_activity_data": "Checking today's activity", "get_sleep_data": "Checking sleep",
          "get_weather": "Checking weather", "get_user_preferences": "Checking preferences",
          "get_recent_meals": "Checking recent meals", "get_current_state": "Checking hunger & time",
          "get_pending_tasks": "Checking pending tasks", "search_food": "Searching food database"}
def ev(tool, label, summary, args=None):
    return {"type": "event", "tool": tool, "label": label or LABELS.get(tool, tool), "summary": summary, "args": args or {}}
def summarize(name, out):
    if name == "get_activity_data": return f"{out['steps']} steps · {out['activity_level']}"
    if name == "get_sleep_data": return f"{out['sleep_hours']} h · {out['sleep_quality']}"
    if name == "get_weather": return f"{out['temperature']}°C · {out['condition']}"
    if name == "get_user_preferences": return f"{out['diet']} · ₹{out['budget']}"
    if name == "get_recent_meals": return ", ".join(m["meal"] for m in out) or "none"
    if name == "get_current_state": return f"hunger {out['hunger']} · {out['local_time']}"
    if name == "get_pending_tasks": return f"{len(out['tasks'])} tasks · {out['available_minutes']} min"
    if name == "search_food": return f"{len(out)} matching items"
    return ""
