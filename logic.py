import hashlib
import json
import os
from datetime import date
from db import get_connection

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def register_full_user(login, password, weight, height, age, gender, activity, target_calories=None, db_path="fitness.db"):
    if not login or len(login.strip()) < 3:
        raise ValueError("Логин должен быть не короче 3 символов")
    if len(password) < 6:
        raise ValueError("Пароль должен быть не короче 6 символов")
    if weight <= 0 or height <= 0 or age <= 0:
        raise ValueError("Вес, рост и возраст должны быть положительными числами")

    conn = get_connection(db_path)
    try:
        with conn:
            # Если пользователь ввел свою норму, сохраняем ее в поле goal
            goal_to_save = str(target_calories) if target_calories and target_calories > 0 else "поддержание"
            conn.execute(
                "INSERT INTO users(login, password_hash, weight, height, age, gender, activity_level, goal) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (login.strip(), hash_password(password), weight, height, age, gender, activity, goal_to_save)
            )
    except Exception:
        raise ValueError("Пользователь с таким логином уже существует")
    finally:
        conn.close()

def login_user(login: str, password: str, db_path="fitness.db") -> int:
    conn = get_connection(db_path)
    row = conn.execute("SELECT id, password_hash FROM users WHERE login = ?", (login.strip(),)).fetchone()
    conn.close()
    if not row or row["password_hash"] != hash_password(password):
        raise ValueError("Неверный логин или пароль")
    return row["id"]

def get_user_profile(user_id: int, db_path="fitness.db") -> dict:
    conn = get_connection(db_path)
    row = conn.execute("SELECT weight, height, age, gender, activity_level, goal FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else {}

def calculate_norm(weight: float, height: float, age: int, gender: str, activity: str, goal: str = "поддержание") -> float:
    # Проверяем, не ввел ли пользователь свою норму (сохраненную в goal)
    try:
        custom_cal = float(goal)
        if custom_cal > 0:
            return custom_cal
    except (ValueError, TypeError):
        pass # Если это не число, считаем по формуле

    if weight <= 0 or height <= 0 or age <= 0: return 0
    if gender.lower() in ["м", "муж", "мужской"]:
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    mults = {"низкая": 1.2, "средняя": 1.55, "высокая": 1.725}
    base_norm = bmr * mults.get(activity, 1.2)
    
    return base_norm

def delete_user(user_id: int, db_path="fitness.db"):
    conn = get_connection(db_path)
    with conn:
        conn.execute("DELETE FROM meal_entries WHERE user_id=?", (user_id,))
        conn.execute("DELETE FROM schedule WHERE user_id=?", (user_id,))
        conn.execute("DELETE FROM workouts WHERE user_id=?", (user_id,))
        templates = conn.execute("SELECT id FROM workout_templates WHERE user_id=?", (user_id,)).fetchall()
        for t in templates:
            conn.execute("DELETE FROM template_exercises WHERE template_id=?", (t["id"],))
        conn.execute("DELETE FROM workout_templates WHERE user_id=?", (user_id,))
        conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.close()

def add_food(name: str, cal: float, prot: float, fat: float, carbs: float, db_path="fitness.db"):
    conn = get_connection(db_path)
    with conn:
        conn.execute("INSERT INTO foods(name, calories_per_100g, protein, fat, carbs) VALUES (?, ?, ?, ?, ?)", (name.strip(), cal, prot, fat, carbs))
    conn.close()

def get_all_foods(db_path="fitness.db"):
    conn = get_connection(db_path)
    rows = conn.execute("SELECT * FROM foods ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def search_foods(query: str, db_path="fitness.db"):
    if not query:
        return get_all_foods(db_path)
    conn = get_connection(db_path)
    rows = conn.execute("SELECT * FROM foods WHERE LOWER(name) LIKE LOWER(?) ORDER BY name LIMIT 15", (f"%{query}%",)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_meal(user_id: int, food_id: int, weight_grams: float, meal_type: str, db_path="fitness.db"):
    conn = get_connection(db_path)
    with conn:
        conn.execute("INSERT INTO meal_entries(user_id, food_id, date, weight_grams, meal_type) VALUES (?, ?, ?, ?, ?)",
                     (user_id, food_id, date.today().isoformat(), weight_grams, meal_type))
    conn.close()

def get_day_nutrition(user_id: int, db_path="fitness.db") -> dict:
    conn = get_connection(db_path)
    rows = conn.execute("""
        SELECT f.calories_per_100g, f.protein, f.fat, f.carbs, m.weight_grams
        FROM meal_entries m JOIN foods f ON f.id = m.food_id
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

def seed_foods(db_path="fitness.db"):
    conn = get_connection(db_path)
    count = conn.execute("SELECT COUNT(*) AS c FROM foods").fetchone()["c"]
    if count == 0:
        json_path = os.path.join("data", "foods.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                foods = json.load(f)
            with conn:
                for food in foods:
                    conn.execute("INSERT INTO foods(name, calories_per_100g, protein, fat, carbs) VALUES (?, ?, ?, ?, ?)",
                                 (food["name"], food["cal"], food["prot"], food["fat"], food["carbs"]))
    conn.close()

def create_template(user_id: int, name: str, db_path="fitness.db") -> int:
    conn = get_connection(db_path)
    with conn:
        cur = conn.execute("INSERT INTO workout_templates(user_id, name) VALUES (?, ?)", (user_id, name.strip()))
        template_id = cur.lastrowid
    conn.close()
    return template_id

def get_user_templates(user_id: int, db_path="fitness.db") -> list:
    conn = get_connection(db_path)
    rows = conn.execute("SELECT * FROM workout_templates WHERE user_id=? ORDER BY name", (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def set_schedule_day(user_id: int, day_of_week: int, template_id: int, db_path="fitness.db"):
    conn = get_connection(db_path)
    with conn:
        conn.execute("DELETE FROM schedule WHERE user_id=? AND day_of_week=?", (user_id, day_of_week))
        conn.execute("INSERT INTO schedule(user_id, day_of_week, template_id) VALUES (?, ?, ?)", (user_id, day_of_week, template_id))
    conn.close()

def get_schedule(user_id: int, db_path="fitness.db") -> dict:
    conn = get_connection(db_path)
    rows = conn.execute("SELECT s.day_of_week, t.name FROM schedule s JOIN workout_templates t ON t.id = s.template_id WHERE s.user_id = ?", (user_id,)).fetchall()
    conn.close()
    return {r["day_of_week"]: r["name"] for r in rows}

def get_recommendations(user_id: int, db_path="fitness.db") -> list:
    conn = get_connection(db_path)
    recs = []
    user = conn.execute("SELECT weight, height, age, gender, activity_level, goal FROM users WHERE id=?", (user_id,)).fetchone()
    if user and user["weight"]:
        norm = calculate_norm(user["weight"], user["height"], user["age"], user["gender"], user["activity_level"] or "низкая", user["goal"])
        today = get_day_nutrition(user_id, db_path)
        if norm > 0 and today["cal"] > 0 and today["cal"] < norm * 0.8:
            recs.append("Вы недоедаете. Это может замедлить прогресс.")
    conn.close()
    return recs if recs else ["Всё отлично! Продолжайте в том же духе."]
def get_all_exercises(db_path="fitness.db"):
    """Возвращает список всех упражнений из справочника."""
    conn = get_connection(db_path)
    rows = conn.execute("SELECT * FROM exercises ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_exercise(name: str, muscle_group: str = "", db_path="fitness.db"):
    """Добавляет новое упражнение в справочник."""
    if not name.strip(): raise ValueError("Название обязательно")
    conn = get_connection(db_path)
    with conn:
        conn.execute("INSERT INTO exercises(name, muscle_group) VALUES (?, ?)", (name.strip(), muscle_group))
    conn.close()

def log_workout_set(workout_id: int, exercise_id: int, sets: int, reps: int, weight: float, db_path="fitness.db"):
    """Сохраняет подход (упражнение, вес, повторения) в журнал тренировки."""
    conn = get_connection(db_path)
    with conn:
        conn.execute(
            "INSERT INTO template_exercises(template_id, exercise_id, sets, reps, weight) VALUES (?, ?, ?, ?, ?)",
            (workout_id, exercise_id, sets, reps, weight)
        )
    conn.close()

def add_exercise_to_template(template_id, exercise_id, sets, reps, weight, db_path="fitness.db"):
    """Добавляет упражнение в шаблон тренировки."""
    conn = get_connection(db_path)
    with conn:
        conn.execute(
            "INSERT INTO template_exercises(template_id, exercise_id, sets, reps, weight) VALUES (?, ?, ?, ?, ?)",
            (template_id, exercise_id, sets, reps, weight)
        )
    conn.close()

def save_workout_set(user_id, exercise_id, sets, reps, weight, db_path="fitness.db"):
    """Сохраняет выполненный подход в историю (для аналитики)."""
    conn = get_connection(db_path)
    with conn:
        conn.execute(
            "INSERT INTO workout_history(user_id, exercise_id, date, sets, reps, weight) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, exercise_id, date.today().isoformat(), sets, reps, weight)
        )
    conn.close()
def get_template_exercises(template_id, db_path="fitness.db"):
    """Возвращает список упражнений, привязанных к шаблону."""
    conn = get_connection(db_path)
    rows = conn.execute("""
        SELECT e.name, te.sets, te.reps, te.weight 
        FROM template_exercises te
        JOIN exercises e ON e.id = te.exercise_id
        WHERE te.template_id = ?
    """, (template_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_exercise_id_by_name(name, db_path="fitness.db"):
    """Находит ID упражнения по его названию."""
    conn = get_connection(db_path)
    row = conn.execute("SELECT id FROM exercises WHERE LOWER(name) = LOWER(?)", (name.strip(),)).fetchone()
    conn.close()
    return row["id"] if row else None