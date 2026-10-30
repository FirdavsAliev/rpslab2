import hashlib
from datetime import date, datetime, timedelta
from db import get_connection

# ================= АВТОРИЗАЦИЯ =================

def hash_password(password: str) -> str:
    """Возвращает SHA-256 хэш пароля."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def register_user(login: str, password: str, db_path="fitness.db"):
    if not login or len(login.strip()) < 3:
        raise ValueError("Логин должен быть не короче 3 символов")
    if len(password) < 6:
        raise ValueError("Пароль должен быть не короче 6 символов")
    
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute(
                "INSERT INTO users(login, password_hash) VALUES (?, ?)",
                (login.strip(), hash_password(password))
            )
    except Exception:
        raise ValueError("Пользователь с таким логином уже существует")
    finally:
        conn.close()

def login_user(login: str, password: str, db_path="fitness.db") -> int:
    """Возвращает ID пользователя при успехе или бросает ошибку."""
    conn = get_connection(db_path)
    row = conn.execute("SELECT id, password_hash FROM users WHERE login = ?", (login.strip(),)).fetchone()
    conn.close()
    
    if not row or row["password_hash"] != hash_password(password):
        raise ValueError("Неверный логин или пароль")
    return row["id"]

def update_user_profile(user_id: int, weight: float, height: float, age: int, gender: str, activity: str, db_path="fitness.db"):
    conn = get_connection(db_path)
    with conn:
        conn.execute(
            "UPDATE users SET weight=?, height=?, age=?, gender=?, activity_level=? WHERE id=?",
            (weight, height, age, gender, activity, user_id)
        )
    conn.close()

# ================= ПРОДУКТЫ И ПИТАНИЕ =================

def add_food(name: str, cal: float, prot: float, fat: float, carbs: float, db_path="fitness.db"):
    if not name.strip():
        raise ValueError("Название продукта не может быть пустым")
    conn = get_connection(db_path)
    with conn:
        conn.execute(
            "INSERT INTO foods(name, calories_per_100g, protein, fat, carbs) VALUES (?, ?, ?, ?, ?)",
            (name.strip(), cal, prot, fat, carbs)
        )
    conn.close()

def get_all_foods(db_path="fitness.db"):
    conn = get_connection(db_path)
    rows = conn.execute("SELECT * FROM foods ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_meal(user_id: int, food_id: int, weight_grams: float, meal_type: str, db_path="fitness.db"):
    if weight_grams <= 0:
        raise ValueError("Вес должен быть больше 0")
    conn = get_connection(db_path)
    with conn:
        conn.execute(
            "INSERT INTO meal_entries(user_id, food_id, date, weight_grams, meal_type) VALUES (?, ?, ?, ?, ?)",
            (user_id, food_id, date.today().isoformat(), weight_grams, meal_type)
        )
    conn.close()

def get_day_nutrition(user_id: int, db_path="fitness.db") -> dict:
    """Считает съеденное за сегодня."""
    conn = get_connection(db_path)
    rows = conn.execute("""
        SELECT f.calories_per_100g, f.protein, f.fat, f.carbs, m.weight_grams
        FROM meal_entries m
        JOIN foods f ON f.id = m.food_id
        WHERE m.user_id = ? AND m.date = ?
    """, (user_id, date.today().isoformat())).fetchall()
    conn.close()
    
    total = {"cal": 0.0, "prot": 0.0, "fat": 0.0, "carbs": 0.0}
    for r in rows:
        k = r["weight_grams"] / 100.0
        total["cal"] += r["calories_per_100g"] * k
        total["prot"] += r["protein"] * k
        total["fat"] += r["fat"] * k
        total["carbs"] += r["carbs"] * k
    return total

def calculate_norm(weight: float, height: float, age: int, gender: str, activity: str) -> float:
    """Формула Миффлина-Сан Жеора для расчета нормы калорий."""
    if gender.lower() in ["м", "муж", "мужской"]:
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
    activity_multipliers = {
        "низкая": 1.2,
        "средняя": 1.55,
        "высокая": 1.725
    }
    mult = activity_multipliers.get(activity, 1.2)
    return bmr * mult

# ================= ТРЕНИРОВКИ =================

def add_exercise(name: str, muscle_group: str, description: str = "", db_path="fitness.db"):
    if not name.strip():
        raise ValueError("Название упражнения обязательно")
    conn = get_connection(db_path)
    with conn:
        conn.execute(
            "INSERT INTO exercises(name, muscle_group, description) VALUES (?, ?, ?)",
            (name.strip(), muscle_group, description)
        )
    conn.close()

def get_all_exercises(db_path="fitness.db"):
    conn = get_connection(db_path)
    rows = conn.execute("SELECT * FROM exercises ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_recommendations(user_id: int, db_path="fitness.db") -> list:
    """Простые правила для рекомендаций."""
    conn = get_connection(db_path)
    recs = []
    
    # Проверка на пропуски тренировок
    workouts = conn.execute(
        "SELECT status, date FROM workouts WHERE user_id = ? ORDER BY date DESC LIMIT 5",
        (user_id,)
    ).fetchall()
    
    missed = sum(1 for w in workouts if w["status"] == "пропущена")
    if missed >= 2:
        recs.append("Вы пропустили несколько тренировок подряд. Попробуйте вернуться в ритм!")
        
    # Проверка на недоедание
    user = conn.execute("SELECT weight, height, age, gender, activity_level FROM users WHERE id=?", (user_id,)).fetchone()
    if user and all(user[k] for k in ["weight", "height", "age", "gender"]):
        norm = calculate_norm(user["weight"], user["height"], user["age"], user["gender"], user["activity_level"] or "низкая")
        today = get_day_nutrition(user_id, db_path)
        if today["cal"] > 0 and today["cal"] < norm * 0.8:
            recs.append("Вы недоедаете. Это может замедлить прогресс.")
            
    conn.close()
    return recs if recs else ["Всё отлично! Продолжайте в том же духе."]