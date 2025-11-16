# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os

app = FastAPI()

# РАЗРЕШИТЬ CORS (ОБЯЗАТЕЛЬНО!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Или только Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация БД
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

@app.post("/api/user")
async def get_user(data: dict):
    telegram_id = data.get("telegram_id")
    if not telegram_id:
        return {"group": None}
    
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT group FROM users WHERE telegram_id = ?", (telegram_id,))
    row = c.fetchone()
    conn.close()
    return {"group": row[0] if row else None}

@app.post("/api/set-group")
async def set_group(data: dict):
    telegram_id = data.get("telegram_id")
    group = data.get("group")
    if not telegram_id or not group:
        return {"status": "error"}
    
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (telegram_id, group) VALUES (?, ?)", (telegram_id, group))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.get("/api/grades")
async def get_grades(group: str = None):
    if not group:
        return []
    # ТУТ ТВОЙ КОД ПАРСИНГА ОЦЕНОК ИЗ KSTU
    # Пример:
    return [
        {"subject": "Математика", "value": 5.0, "date": "15.11"},
        {"subject": "Физика", "value": 4.0, "date": "14.11"}
    ]

# Для Railway
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))