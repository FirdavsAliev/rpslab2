import tkinter as tk
from tkinter import ttk, messagebox
import logic
import db

# Цвета в стиле iOS
BG_COLOR = "#F2F2F7"       # Светло-серый фон
CARD_COLOR = "#FFFFFF"     # Белые карточки
TEXT_COLOR = "#000000"
ACCENT_COLOR = "#007AFF"   # Синий iOS

class FitnessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fitness Tracker")
        self.root.geometry("450x750") # Размер как у телефона
        self.root.configure(bg=BG_COLOR)
        
        self.current_user_id = None
        db.init_db()
        self.show_login_screen()

    # --- Утилиты дизайна ---
    def create_card(self, parent, title, text=""):
        card = tk.Frame(parent, bg=CARD_COLOR, bd=0, highlightthickness=0)
        card.pack(fill="x", pady=5, padx=15)
        tk.Label(card, text=title, font=("Helvetica", 14, "bold"), bg=CARD_COLOR, fg=TEXT_COLOR).pack(anchor="w", padx=15, pady=(10, 0))
        if text:
            tk.Label(card, text=text, font=("Helvetica", 12), bg=CARD_COLOR, fg="gray").pack(anchor="w", padx=15, pady=(0, 10))
        return card

    # --- Экраны ---
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self.clear_window()
        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(expand=True, fill="both", padx=30)

        tk.Label(frame, text="Fitness Tracker", font=("Helvetica", 24, "bold"), bg=BG_COLOR).pack(pady=(50, 30))

        tk.Label(frame, text="Логин", bg=BG_COLOR, font=("Helvetica", 12)).pack(anchor="w")
        self.login_entry = tk.Entry(frame, font=("Helvetica", 14), bg="white", bd=1, relief="solid")
        self.login_entry.pack(fill="x", pady=(5, 15), ipady=8)

        tk.Label(frame, text="Пароль", bg=BG_COLOR, font=("Helvetica", 12)).pack(anchor="w")
        self.pass_entry = tk.Entry(frame, show="*", font=("Helvetica", 14), bg="white", bd=1, relief="solid")
        self.pass_entry.pack(fill="x", pady=(5, 20), ipady=8)

        tk.Button(frame, text="Войти", command=self.do_login, bg=ACCENT_COLOR, fg="white", font=("Helvetica", 14, "bold"), bd=0).pack(fill="x", ipady=10, pady=5)
        tk.Button(frame, text="Регистрация", command=self.do_register, bg="white", fg=ACCENT_COLOR, font=("Helvetica", 14), bd=1, relief="solid").pack(fill="x", ipady=10)

    def do_login(self):
        try:
            self.current_user_id = logic.login_user(self.login_entry.get(), self.pass_entry.get())
            self.show_main_screen()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def do_register(self):
        try:
            logic.register_user(self.login_entry.get(), self.pass_entry.get())
            messagebox.showinfo("Успех", "Аккаунт создан! Теперь войдите.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def show_main_screen(self):
        self.clear_window()
        
        # Верхняя панель
        top = tk.Frame(self.root, bg=BG_COLOR, pady=15)
        top.pack(fill="x")
        tk.Label(top, text="Мой день", font=("Helvetica", 20, "bold"), bg=BG_COLOR).pack(side="left", padx=15)
        tk.Button(top, text="Выйти", command=self.show_login_screen, bg=BG_COLOR, fg="red", font=("Helvetica", 12), bd=0).pack(side="right", padx=15)

        # Нижнее меню (как в iOS)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.tab_home = tk.Frame(self.notebook, bg=BG_COLOR)
        self.tab_profile = tk.Frame(self.notebook, bg=BG_COLOR)
        self.tab_nutrition = tk.Frame(self.notebook, bg=BG_COLOR)
        self.tab_workouts = tk.Frame(self.notebook, bg=BG_COLOR)

        self.notebook.add(self.tab_home, text="🏠 Главная")
        self.notebook.add(self.tab_nutrition, text="🍎 Питание")
        self.notebook.add(self.tab_workouts, text="🏋️ Тренировки")
        self.notebook.add(self.tab_profile, text="👤 Профиль")

        self.build_home_tab()
        self.build_nutrition_tab()
        self.build_workouts_tab()
        self.build_profile_tab()

    # --- Вкладка Главная ---
    def build_home_tab(self):
        scroll = tk.Frame(self.tab_home, bg=BG_COLOR)
        scroll.pack(fill="both", expand=True, pady=10)

        today = logic.get_day_nutrition(self.current_user_id)
        self.create_card(scroll, "Калории сегодня", f"Съедено: {today['cal']:.0f} ккал\nБ: {today['prot']:.1f} | Ж: {today['fat']:.1f} | У: {today['carbs']:.1f}")

        recs = logic.get_recommendations(self.current_user_id)
        rec_text = "\n".join([f"• {r}" for r in recs])
        self.create_card(scroll, "Совет дня", rec_text)

        schedule = logic.get_schedule(self.current_user_id)
        sched_text = "Сегодня тренировки нет. Отдыхайте!" if not schedule else "Посмотрите расписание в разделе Тренировки."
        self.create_card(scroll, "Тренировки", sched_text)

    # --- Вкладка Профиль ---
    def build_profile_tab(self):
        profile = logic.get_user_profile(self.current_user_id)
        frame = tk.Frame(self.tab_profile, bg=BG_COLOR, padx=15, pady=15)
        frame.pack(fill="both", expand=True)

        self.p_weight = self._add_input(frame, "Вес (кг):", profile.get("weight"))
        self.p_height = self._add_input(frame, "Рост (см):", profile.get("height"))
        self.p_age = self._add_input(frame, "Возраст:", profile.get("age"))

        tk.Button(frame, text="Сохранить профиль", command=self.save_profile, bg=ACCENT_COLOR, fg="white", bd=0, font=("Helvetica", 12, "bold")).pack(fill="x", pady=20, ipady=8)

    def _add_input(self, parent, label, default_val):
        tk.Label(parent, text=label, bg=BG_COLOR, font=("Helvetica", 12)).pack(anchor="w", pady=(10, 0))
        entry = tk.Entry(parent, font=("Helvetica", 14), bg="white", bd=1, relief="solid")
        if default_val: entry.insert(0, str(default_val))
        entry.pack(fill="x", pady=(5, 0), ipady=5)
        return entry

    def save_profile(self):
        try:
            logic.update_user_profile(self.current_user_id, float(self.p_weight.get()), float(self.p_height.get()), int(self.p_age.get()), "муж", "средняя")
            messagebox.showinfo("Успех", "Профиль сохранен!")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # --- Вкладка Питание ---
    def build_nutrition_tab(self):
        frame = tk.Frame(self.tab_nutrition, bg=BG_COLOR, padx=15, pady=15)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Добавить еду", bg=BG_COLOR, font=("Helvetica", 14, "bold")).pack(anchor="w")
        
        self.food_combo = ttk.Combobox(frame, font=("Helvetica", 12))
        self.food_combo['values'] = [f["name"] for f in logic.get_all_foods()]
        self.food_combo.pack(fill="x", pady=5)

        tk.Label(frame, text="Вес (грамм):", bg=BG_COLOR).pack(anchor="w")
        self.weight_entry = tk.Entry(frame, font=("Helvetica", 14), bg="white")
        self.weight_entry.pack(fill="x", pady=5, ipady=5)

        tk.Button(frame, text="Добавить в дневник", command=self.add_meal, bg=ACCENT_COLOR, fg="white", bd=0).pack(fill="x", pady=10, ipady=8)

        self.nutrition_summary = tk.Label(frame, text="", bg=BG_COLOR, justify="left")
        self.nutrition_summary.pack(anchor="w", pady=10)
        self.update_nutrition_summary()

    def add_meal(self):
        try:
            foods = logic.get_all_foods()
            food_id = next(f["id"] for f in foods if f["name"] == self.food_combo.get())
            logic.add_meal(self.current_user_id, food_id, float(self.weight_entry.get()), "прием")
            self.update_nutrition_summary()
            messagebox.showinfo("Успех", "Добавлено!")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def update_nutrition_summary(self):
        data = logic.get_day_nutrition(self.current_user_id)
        self.nutrition_summary.config(text=f"Итого за день:\nКалории: {data['cal']:.1f}\nБелки: {data['prot']:.1f}\nЖиры: {data['fat']:.1f}\nУглеводы: {data['carbs']:.1f}")

    # --- Вкладка Тренировки ---
    def build_workouts_tab(self):
        frame = tk.Frame(self.tab_workouts, bg=BG_COLOR, padx=15, pady=15)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Создать тренировку", bg=BG_COLOR, font=("Helvetica", 14, "bold")).pack(anchor="w")
        self.template_name = tk.Entry(frame, font=("Helvetica", 14), bg="white")
        self.template_name.pack(fill="x", pady=5, ipady=5)
        tk.Button(frame, text="Создать шаблон", command=self.create_template, bg=ACCENT_COLOR, fg="white", bd=0).pack(fill="x", pady=5, ipady=5)

        tk.Label(frame, text="Мои шаблоны:", bg=BG_COLOR, font=("Helvetica", 12)).pack(anchor="w", pady=(15,0))
        self.templates_listbox = tk.Listbox(frame, font=("Helvetica", 12), bg="white", bd=0)
        self.templates_listbox.pack(fill="both", expand=True, pady=5)
        self.refresh_templates()

    def create_template(self):
        try:
            logic.create_template(self.current_user_id, self.template_name.get())
            self.refresh_templates()
            self.template_name.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def refresh_templates(self):
        self.templates_listbox.delete(0, tk.END)
        for t in logic.get_user_templates(self.current_user_id):
            self.templates_listbox.insert(tk.END, t["name"])

if __name__ == "__main__":
    root = tk.Tk()
    app = FitnessApp(root)
    root.mainloop()