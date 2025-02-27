from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

# Загрузите переменные окружения из .env
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Разрешенные домены
    allow_credentials=True,
    allow_methods=["*"],  # Разрешенные методы
    allow_headers=["*"],  # Разрешенные заголовки
)

# Инициализация Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Модель для кота
class Cat(BaseModel):
    name: str
    age: int
    description: str
    avatar: str
    breed: str
    color: str
    passport_url: str

# Модель для ответа с id
class CatResponse(Cat):
    id: int

# Роуты
@app.post("/cats/", response_model=CatResponse)
async def create_cat(cat: Cat):
    # Вставляем данные в таблицу "cats"
    data, count = supabase.table("cats").insert(cat.dict()).execute()
    if data:
        # Возвращаем данные с id
        return data[1][0]
    raise HTTPException(status_code=500, detail="Failed to create cat")

@app.get("/cats/{cat_id}", response_model=CatResponse)
async def read_cat(cat_id: int):
    # Получаем кота по ID
    data, count = supabase.table("cats").select("*").eq("id", cat_id).execute()
    if data[1]:
        return data[1][0]
    raise HTTPException(status_code=404, detail="Cat not found")

@app.put("/cats/{cat_id}", response_model=CatResponse)
async def update_cat(cat_id: int, cat: Cat):
    # Обновляем данные кота
    data, count = supabase.table("cats").update(cat.dict()).eq("id", cat_id).execute()
    if data[1]:
        return data[1][0]
    raise HTTPException(status_code=404, detail="Cat not found")

@app.delete("/cats/{cat_id}")
async def delete_cat(cat_id: int):
    # Удаляем кота по ID
    data, count = supabase.table("cats").delete().eq("id", cat_id).execute()
    if count[1]:
        return {"message": "Cat deleted"}
    raise HTTPException(status_code=404, detail="Cat not found")

@app.get("/cats/", response_model=list[CatResponse])
async def read_all_cats():
    # Получаем всех котов
    data, count = supabase.table("cats").select("*").execute()
    return data[1]