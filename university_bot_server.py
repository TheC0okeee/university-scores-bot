from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import uvicorn
import os

app = FastAPI(title="KSTU Track API")

# CORS — РАЗРЕШИТЬ ВСЁ
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ИНИЦИАЛИЗАЦИЯ БД
def init_db():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            "group" TEXT,
            notifications INTEGER DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ГЛАВНАЯ СТРАНИЦА
@app.get("/")
async def root():
    return {"message": "KSTU Track API работает!"}

# ПОЛУЧИТЬ ГРУППУ ПОЛЬЗОВАТЕЛЯ
@app.post("/api/user")
async def get_user(request: Request):
    data = await request.json()
    telegram_id = data.get("telegram_id")
    if not telegram_id:
        return {"error": "telegram_id required"}
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT "group" FROM users WHERE telegram_id = ?', (telegram_id,))
    row = c.fetchone()
    conn.close()
    return {"group": row[0] if row else None}

# УСТАНОВИТЬ ГРУППУ
@app.post("/api/set-group")
async def set_group(request: Request):
    data = await request.json()
    telegram_id = data.get("telegram_id")
    group = data.get("group")
    if not telegram_id or not group:
        return {"error": "telegram_id and group required"}
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO users (telegram_id, "group") VALUES (?, ?)', (telegram_id, group))
    conn.commit()
    conn.close()
    return {"status": "ok"}

# ЗАГЛУШКА ОЦЕНОК
@app.get("/api/grades")
async def get_grades(group: str = None):
    if not group:
        return []
    return [
        {"subject": "Математика", "value": 5.0, "date": "16.11.2025"},
        {"subject": "Физика", "value": 4.0, "date": "15.11.2025"}
    ]

# ЗАПУСК ДЛЯ RAILWAY
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
