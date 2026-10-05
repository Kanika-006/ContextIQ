"""Real callable tools. Each takes the user's (simulated) context `ctx` so a real
wearable / weather / calendar API can replace any one function without touching the agent."""
from data.foods import FOODS

DIETS = {"vegetarian", "non-vegetarian", "any"}
def diet_of(ctx):  # normalised diet; unknown values default to the safest option
    d = str(ctx.get("diet", "vegetarian")).strip().lower()
    return d if d in DIETS else "vegetarian"

def get_activity_data(ctx):
    s = ctx["steps"]
    return {"steps": s, "activity_level": "high" if s >= 7000 else "moderate" if s >= 4000 else "low"}

def get_sleep_data(ctx):
    h = ctx["sleep_hours"]
    return {"sleep_hours": h, "sleep_quality": "good" if h >= 7 else "fair" if h >= 6 else "poor"}

def get_weather(ctx):  # swap for a real weather API call
    t = ctx.get("temperature", 27)
    return {"temperature": t, "condition": "clear" if t > 15 else "cool", "rain_probability": 10}

def get_user_preferences(ctx):
    return {"diet": diet_of(ctx), "budget": ctx["budget"],
            "preferred_cuisines": ["Indian", "North Indian"], "disliked_foods": ["very spicy"]}

def get_recent_meals(ctx):
    return ctx["recent_meals"]

def get_current_state(ctx):
    return {"hunger": ctx["hunger"], "local_time": ctx["time"]}

def get_pending_tasks(ctx):
    return {"tasks": ctx["tasks"], "available_minutes": ctx["available_minutes"], "start_time": ctx["time"]}

def search_food(ctx, vegetarian=None,  # `vegetarian` is ignored: the user's diet (ctx) is enforced here
                max_price=None, min_protein=None, min_calories=None,
                max_calories=None, max_spice=None, cuisine=None, query=None, limit=50):
    diet, out = diet_of(ctx), []
    for f in FOODS:
        if diet == "vegetarian" and not f["vegetarian"]: continue
        if diet == "non-vegetarian" and f["vegetarian"]: continue
        if max_price is not None and f["price"] > max_price: continue
        if min_protein is not None and f["protein"] < min_protein: continue
        if min_calories is not None and f["calories"] < min_calories: continue
        if max_calories is not None and f["calories"] > max_calories: continue
        if max_spice is not None and f["spice_level"] > max_spice: continue
        if cuisine and cuisine.lower() not in f["cuisine"].lower(): continue
        if query and query.lower() not in (f["name"] + f["category"]).lower(): continue
        out.append(f)
    return out[:int(limit)]

def get_food(item_id):
    return next((f for f in FOODS if f["id"] == item_id), None)

def add_to_cart(cart, item_id):
    item = get_food(item_id)
    if not item: return {"ok": False, "error": f"unknown item_id {item_id}"}
    cart.append({"id": item["id"], "name": item["name"], "price": item["price"]})
    return {"ok": True, "item": item["name"], "cart_total": sum(c["price"] for c in cart)}

READ_TOOLS = {"get_activity_data": get_activity_data, "get_sleep_data": get_sleep_data,
              "get_weather": get_weather, "get_user_preferences": get_user_preferences,
              "get_recent_meals": get_recent_meals, "get_current_state": get_current_state,
              "get_pending_tasks": get_pending_tasks, "search_food": search_food}
