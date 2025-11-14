import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson.objectid import ObjectId

from database import db, create_document, get_documents
from schemas import Cafe, MenuItem, Order, Reservation

app = FastAPI(title="Cafe API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Cafe API is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set"
            response["database_name"] = getattr(db, 'name', '✅ Connected')
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "❌ Not Available"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# ----------------------- Helpers -----------------------

def to_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

# ----------------------- Cafe -----------------------

@app.post("/api/cafes")
async def create_cafe(cafe: Cafe):
    inserted_id = create_document("cafe", cafe)
    return {"id": inserted_id}

@app.get("/api/cafes")
async def list_cafes():
    docs = get_documents("cafe")
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs

# ----------------------- Menu -----------------------

@app.post("/api/menu")
async def create_menu_item(item: MenuItem):
    inserted_id = create_document("menuitem", item)
    return {"id": inserted_id}

@app.get("/api/menu")
async def list_menu():
    docs = get_documents("menuitem")
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs

# ----------------------- Orders (Buy) -----------------------

class CreateOrderRequest(Order):
    pass

@app.post("/api/orders")
async def create_order(order: CreateOrderRequest):
    # compute total from menu items
    items = []
    total = 0.0
    for it in order.items:
        mid = to_object_id(it.menu_item_id)
        doc = db["menuitem"].find_one({"_id": mid})
        if not doc:
            raise HTTPException(status_code=404, detail="Menu item not found")
        price = float(doc.get("price", 0))
        total += price * it.quantity
        items.append({"menu_item_id": it.menu_item_id, "quantity": it.quantity, "price": price})
    payload = order.model_dump()
    payload["items"] = items
    payload["total"] = round(total, 2)
    inserted_id = create_document("order", payload)
    return {"id": inserted_id, "total": payload["total"]}

@app.get("/api/orders")
async def list_orders():
    docs = get_documents("order")
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs

# ----------------------- Reservations -----------------------

@app.post("/api/reservations")
async def create_reservation(res: Reservation):
    inserted_id = create_document("reservation", res)
    return {"id": inserted_id}

@app.get("/api/reservations")
async def list_reservations():
    docs = get_documents("reservation")
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
