from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sqlite3
import json
import os

app = FastAPI(title="KSTU Track API", description="API for Telegram Mini App")

# CORS — РАЗРЕШИТЬ ЗАПРОСЫ ИЗ MINI APP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# БАЗА ДАННЫХ
def init_db():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            group TEXT,
            notifications INTEGER DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# === API ЭНДПОИНТЫ ===

@app.get("/")
async def root():
    return {"message": "KSTU Track API работает!", "endpoints": ["/api/user", "/api/set-group", "/api/grades"]}

@app.post("/api/user")
async def get_user(request: Request):
    data = await request.json()
    telegram_id = data.get("telegram_id")
    if not telegram_id:
        return JSONResponse(status_code=400, content={"error": "telegram_id required"})
    
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT group FROM users WHERE telegram_id = ?", (telegram_id,))
    row = c.fetchone()
    conn.close()
    return {"group": row[0] if row else None}

@app.post("/api/set-group")
async def set_group(request: Request):
    data = await request.json()
    telegram_id = data.get("telegram_id")
    group = data.get("group")
    if not telegram_id or not group:
        return JSONResponse(status_code=400, content={"error": "telegram_id and group required"})
    
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (telegram_id, group) VALUES (?, ?)", (telegram_id, group))
    conn.commit()
    conn.close()
    return {"status": "ok", "group": group}

@app.get("/api/grades")
async def get_grades(group: str = None):
    if not group:
        return []
    
    # МОК-ОЦЕНКИ (замени на реальный парсинг)
    return [
        {"subject": "Высшая математика", "value": 5.0, "date": "15.11.2025"},
        {"subject": "Информатика", "value": 4.0, "date": "14.11.2025"}
    ]

# Для Railway
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)