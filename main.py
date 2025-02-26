from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

app = FastAPI()

# Подключение к MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.catdb
cats_collection = db.cats

# Модель для кота
class Cat(BaseModel):
    name: str
    age: int
    description: str
    avatar: str
    breed: str
    color: str
    passport_url: str

# Роуты
@app.post("/cats/", response_model=Cat)
async def create_cat(cat: Cat):
    cat_dict = cat.dict()
    await cats_collection.insert_one(cat_dict)
    return cat

@app.get("/cats/{cat_id}", response_model=Cat)
async def read_cat(cat_id: str):
    cat = await cats_collection.find_one({"_id": ObjectId(cat_id)})
    if cat:
        return cat
    raise HTTPException(status_code=404, detail="Cat not found")

@app.put("/cats/{cat_id}", response_model=Cat)
async def update_cat(cat_id: str, cat: Cat):
    await cats_collection.update_one({"_id": ObjectId(cat_id)}, {"$set": cat.dict()})
    updated_cat = await cats_collection.find_one({"_id": ObjectId(cat_id)})
    if updated_cat:
        return updated_cat
    raise HTTPException(status_code=404, detail="Cat not found")

@app.delete("/cats/{cat_id}")
async def delete_cat(cat_id: str):
    result = await cats_collection.delete_one({"_id": ObjectId(cat_id)})
    if result.deleted_count:
        return {"message": "Cat deleted"}
    raise HTTPException(status_code=404, detail="Cat not found")

@app.get("/cats/", response_model=list[Cat])
async def read_all_cats():
    cats = await cats_collection.find().to_list(100)
    return cats