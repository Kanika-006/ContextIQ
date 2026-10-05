import os, json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
import tools as T, fallback
from events import ev

app = FastAPI(title="ContextIQ")
CART = []
FRONT = Path(__file__).resolve().parent.parent / "frontend" / "index.html"

class AgentReq(BaseModel):
    mode: str = "food"            # food | evening
    goal: str = "What should I order for dinner tonight?"
    context: dict
    force_fallback: bool = False

def stream(req):
    use_llm = bool(os.getenv("GEMINI_API_KEY")) and not req.force_fallback
    done = False
    if use_llm:
        try:
            import agent
            for e in agent.run(req.mode, req.goal, req.context):
                done = done or e["type"] == "result"
                yield json.dumps(e) + "\n"
            return
        except Exception as ex:
            if done: return
            yield json.dumps(ev(None, "LLM unavailable — switching to rule-based fallback", str(ex)[:140])) + "\n"
    else:
        yield json.dumps(ev(None, "No LLM key / fallback forced", "using rule-based fallback")) + "\n"
    try:
        for e in (fallback.run_food if req.mode == "food" else fallback.run_evening)(req.context):
            yield json.dumps(e) + "\n"
    except Exception as ex:
        yield json.dumps({"type": "error", "message": f"Fallback failed: {ex}"}) + "\n"

@app.post("/api/agent")
def run_agent(req: AgentReq):
    return StreamingResponse(stream(req), media_type="application/x-ndjson")

class CartReq(BaseModel):
    item_id: int

@app.post("/api/cart/add")   # the action tool, called only after the user clicks Add to Cart
def cart_add(r: CartReq):
    res = T.add_to_cart(CART, r.item_id)
    return {**res, "cart": CART, "total": sum(c["price"] for c in CART)}

@app.get("/api/cart")
def cart_get(): return {"cart": CART, "total": sum(c["price"] for c in CART)}

@app.delete("/api/cart")
def cart_clear(): CART.clear(); return {"cart": [], "total": 0}

@app.get("/api/health")
def health(): return {"llm_configured": bool(os.getenv("GEMINI_API_KEY"))}

@app.get("/")
def index(): return FileResponse(FRONT)
