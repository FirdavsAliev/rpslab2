import tkinter as tk
from tkinter import ttk, messagebox
import logic
import db
import styles
from styles import BG_COLOR, CARD_COLOR, ACCENT_COLOR, GRAY_TEXT, TEXT_COLOR, PROGRESS_BG, PROGRESS_FILL, PROGRESS_OVER

class FitnessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fitness Tracker")
        self.root.geometry("450x800")
        self.root.configure(bg=BG_COLOR)
        
        self.current_user_id = None
        db.init_db()
        logic.seed_foods()
        self.show_welcome_screen()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def _create_input(self, parent, label, show=None):
        tk.Label(parent, text=label, bg=BG_COLOR, font=("Helvetica", 12)).pack(anchor="w", pady=(5, 0))
        entry = tk.Entry(parent, font=("Helvetica", 14), bg="white", show=show if show else "")
        entry.pack(fill="x", pady=(2, 5), ipady=5)
        return entry

    # --- 1. ЭКРАН ПРИВЕТСТВИЯ ---
    def show_welcome_screen(self):
        self.clear()
        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(expand=True, fill="both", padx=30)

        center_frame = tk.Frame(frame, bg=BG_COLOR)
        center_frame.pack(expand=True)

        tk.Label(center_frame, text="Добро пожаловать\nв Fitness Tracker!", font=("Helvetica", 22, "bold"), bg=BG_COLOR, justify="center").pack(pady=(0, 40))
        
        tk.Button(center_frame, text="Начать (Регистрация)", command=self.show_registration_screen, bg=ACCENT_COLOR, fg="white", font=("Helvetica", 14, "bold"), bd=0).pack(fill="x", ipady=10, pady=5)
        tk.Button(center_frame, text="У меня уже есть аккаунт", command=self.show_login_screen, bg="white", fg=ACCENT_COLOR, font=("Helvetica", 14), bd=1, relief="solid").pack(fill="x", ipady=10, pady=5)

    # --- 2. ЭКРАН ВХОДА ---
    def show_login_screen(self):
        self.clear()
        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(expand=True, fill="both", padx=30, pady=50)
        tk.Label(frame, text="Вход", font=("Helvetica", 24, "bold"), bg=BG_COLOR).pack(pady=(50, 30))
        self.login_entry = self._create_input(frame, "Логин")
        self.pass_entry = self._create_input(frame, "Пароль", show="*")
        tk.Button(frame, text="Войти", command=self.do_login, bg=ACCENT_COLOR, fg="white", font=("Helvetica", 14, "bold"), bd=0).pack(fill="x", ipady=10, pady=10)
        tk.Button(frame, text="Назад", command=self.show_welcome_screen, bg=BG_COLOR, fg=ACCENT_COLOR, font=("Helvetica", 12), bd=0).pack()

    def do_login(self):
        try:
            self.current_user_id = logic.login_user(self.login_entry.get(), self.pass_entry.get())
            self.show_main_screen()
        except Exception as e:
            messagebox.showerror("Ошибка входа", str(e))

    # --- 3. ЭКРАН РЕГИСТРАЦИИ ---
    def show_registration_screen(self):
        self.clear()
        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(expand=True, fill="both", padx=30, pady=20)
        tk.Label(frame, text="Создание профиля", font=("Helvetica", 20, "bold"), bg=BG_COLOR).pack(pady=(20, 10))
        
        self.reg_login = self._create_input(frame, "Придумайте логин")
        self.reg_pass = self._create_input(frame, "Придумайте пароль (мин. 6 симв.)", show="*")
        self.reg_weight = self._create_input(frame, "Вес (кг)")
        self.reg_height = self._create_input(frame, "Рост (см)")
        self.reg_age = self._create_input(frame, "Возраст (лет)")
        self.reg_target_cal = self._create_input(frame, "Своя норма калорий (ккал) - необязательно")

        tk.Label(frame, text="Пол", bg=BG_COLOR, font=("Helvetica", 12)).pack(anchor="w", pady=(5, 0))
        self.gender_var = tk.StringVar(value="муж")
        g_frame = tk.Frame(frame, bg=BG_COLOR)
        g_frame.pack(fill="x")
        tk.Radiobutton(g_frame, text="Мужской", variable=self.gender_var, value="муж", bg=BG_COLOR).pack(side="left")
        tk.Radiobutton(g_frame, text="Женский", variable=self.gender_var, value="жен", bg=BG_COLOR).pack(side="left")

        tk.Label(frame, text="Активность", bg=BG_COLOR, font=("Helvetica", 12)).pack(anchor="w", pady=(5, 0))
        self.activity_combo = ttk.Combobox(frame, values=["низкая", "средняя", "высокая"], state="readonly")
        self.activity_combo.current(1)
        self.activity_combo.pack(fill="x", pady=2)

        tk.Button(frame, text="Завершить и войти", command=self.do_full_registration, bg=ACCENT_COLOR, fg="white", font=("Helvetica", 14, "bold"), bd=0).pack(fill="x", ipady=10, pady=15)

    def do_full_registration(self):
        try:
            target_cal = None
            cal_input = self.reg_target_cal.get().strip()
            if cal_input:
                try:
                    target_cal = float(cal_input)
                except ValueError:
                    messagebox.showwarning("Ошибка", "Норма калорий должна быть числом (например, 2500).")
                    return

            logic.register_full_user(
                login=self.reg_login.get(), password=self.reg_pass.get(),
                weight=float(self.reg_weight.get()), height=float(self.reg_height.get()),
                age=int(self.reg_age.get()), gender=self.gender_var.get(),
                activity=self.activity_combo.get(), target_calories=target_cal
            )
            self.current_user_id = logic.login_user(self.reg_login.get(), self.reg_pass.get())
            messagebox.showinfo("Успех", "Профиль создан!")
            self.show_main_screen()
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте, что вес, рост и возраст — это числа.")
        except Exception as e:
            messagebox.showerror("Ошибка регистрации", str(e))

    # --- 4. ГЛАВНЫЙ ЭКРАН ---
    def show_main_screen(self):
        self.clear()
        top = tk.Frame(self.root, bg=BG_COLOR, pady=15)
        top.pack(fill="x")
        tk.Label(top, text="Мой день", font=("Helvetica", 20, "bold"), bg=BG_COLOR).pack(side="left", padx=15)
        tk.Button(top, text="Выйти", command=self.show_welcome_screen, bg=BG_COLOR, fg="red", font=("Helvetica", 12), bd=0).pack(side="right", padx=15)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.tab_home = tk.Frame(self.notebook, bg=BG_COLOR)
        self.tab_nutrition = tk.Frame(self.notebook, bg=BG_COLOR)
        self.tab_workouts = tk.Frame(self.notebook, bg=BG_COLOR)
        self.tab_profile = tk.Frame(self.notebook, bg=BG_COLOR)

        self.notebook.add(self.tab_home, text="🏠 Главная")
        self.notebook.add(self.tab_nutrition, text="🍎 Питание")
        self.notebook.add(self.tab_workouts, text="🏋️ Тренировки")
        self.notebook.add(self.tab_profile, text="👤 Профиль")

        self.build_home_tab()
        self.build_nutrition_tab()
        self.build_workouts_tab()
        self.build_profile_tab()

    # --- ГЛАВНАЯ (НОВЫЙ ДИЗАЙН) ---
    def build_home_tab(self):
        for widget in self.tab_home.winfo_children():
            widget.destroy()

        canvas = tk.Canvas(self.tab_home, bg=BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_home, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=BG_COLOR)
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=420)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        profile = logic.get_user_profile(self.current_user_id)
        self.norm_cal = logic.calculate_norm(profile["weight"], profile["height"], profile["age"], profile["gender"], profile["activity_level"], profile["goal"])
        today = logic.get_day_nutrition(self.current_user_id)
        
        # КРУГ
        card_cal = tk.Frame(scroll_frame, bg=CARD_COLOR, bd=0)
        card_cal.pack(fill="x", pady=10, padx=15)
        tk.Label(card_cal, text="Калории", font=("Helvetica", 14, "bold"), bg=CARD_COLOR).pack(anchor="w", padx=15, pady=(10, 0))
        
        canvas_cal = tk.Canvas(card_cal, width=200, height=200, bg=CARD_COLOR, highlightthickness=0)
        canvas_cal.pack(pady=10)
        canvas_cal.create_oval(20, 20, 180, 180, outline=PROGRESS_BG, width=15)
        
        percent = min(today['cal'] / self.norm_cal, 1.0) if self.norm_cal > 0 else 0
        color = PROGRESS_OVER if today['cal'] > self.norm_cal else PROGRESS_FILL
        if percent > 0:
            canvas_cal.create_arc(20, 20, 180, 180, start=90, extent=-percent*360, outline=color, width=15, style="arc")
        
        canvas_cal.create_text(100, 90, text=f"{today['cal']:.0f}", font=("Helvetica", 24, "bold"), fill=TEXT_COLOR)
        canvas_cal.create_text(100, 115, text=f"из {self.norm_cal:.0f} ккал", font=("Helvetica", 10), fill=GRAY_TEXT)
        
        left_cal = max(0, self.norm_cal - today['cal'])
        tk.Label(card_cal, text=f"Осталось: {left_cal:.0f} ккал", font=("Helvetica", 12), bg=CARD_COLOR, fg=GRAY_TEXT).pack(pady=(0, 10))

        # БЖУ
        n_prot, n_fat, n_carb = self.calculate_macros(self.norm_cal, profile["goal"])
        card_macros = tk.Frame(scroll_frame, bg=CARD_COLOR, bd=0)
        card_macros.pack(fill="x", pady=10, padx=15)
        tk.Label(card_macros, text="БЖУ", font=("Helvetica", 14, "bold"), bg=CARD_COLOR).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.draw_progress_bar(card_macros, "Белки", today['prot'], n_prot, "г")
        self.draw_progress_bar(card_macros, "Жиры", today['fat'], n_fat, "г")
        self.draw_progress_bar(card_macros, "Углеводы", today['carbs'], n_carb, "г")

        # ТРЕНИРОВКА
        import datetime
        schedule = logic.get_schedule(self.current_user_id)
        today_weekday = datetime.datetime.today().isoweekday()
        
        card_sport = tk.Frame(scroll_frame, bg=CARD_COLOR, bd=0)
        card_sport.pack(fill="x", pady=10, padx=15)
        
        if today_weekday in schedule:
            tk.Label(card_sport, text="🏋️ Тренировка сегодня", font=("Helvetica", 14, "bold"), bg=CARD_COLOR).pack(anchor="w", padx=15, pady=(10, 0))
            tk.Label(card_sport, text=schedule[today_weekday], font=("Helvetica", 12), bg=CARD_COLOR, fg=ACCENT_COLOR).pack(anchor="w", padx=15, pady=(0, 10))
        else:
            tk.Label(card_sport, text="💡 Совет дня", font=("Helvetica", 14, "bold"), bg=CARD_COLOR).pack(anchor="w", padx=15, pady=(10, 0))
            recs = logic.get_recommendations(self.current_user_id)
            tk.Label(card_sport, text="\n".join(recs), font=("Helvetica", 12), bg=CARD_COLOR, fg=GRAY_TEXT, justify="left").pack(anchor="w", padx=15, pady=(0, 10))

    def draw_progress_bar(self, parent, label, current, target, unit):
        frame = tk.Frame(parent, bg=CARD_COLOR)
        frame.pack(fill="x", padx=15, pady=5)
        text = f"{label}: {current:.1f} / {target:.1f} {unit}"
        tk.Label(frame, text=text, bg=CARD_COLOR, font=("Helvetica", 11)).pack(anchor="w")
        canvas = tk.Canvas(frame, height=8, bg=PROGRESS_BG, highlightthickness=0)
        canvas.pack(fill="x", pady=(2, 5))
        percent = min(current / target, 1.0) if target > 0 else 0
        color = PROGRESS_OVER if current > target else PROGRESS_FILL
        def draw_rect(event):
            canvas.delete("all")
            canvas.create_rectangle(0, 0, event.width * percent, 8, fill=color, outline="")
        canvas.bind("<Configure>", draw_rect)

    def calculate_macros(self, calories, goal):
        if goal == "похудение": p, f, c = 0.40, 0.20, 0.40
        elif goal == "набор массы": p, f, c = 0.25, 0.25, 0.50
        else: p, f, c = 0.30, 0.30, 0.40
        return (calories * p) / 4, (calories * f) / 9, (calories * c) / 4

    # --- ПИТАНИЕ ---
    def build_nutrition_tab(self):
        frame = tk.Frame(self.tab_nutrition, bg=BG_COLOR, padx=15, pady=15)
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text="Добавить еду", bg=BG_COLOR, font=("Helvetica", 14, "bold")).pack(anchor="w")
        tk.Label(frame, text="Поиск продукта:", bg=BG_COLOR).pack(anchor="w")
        self.food_combo = ttk.Combobox(frame, font=("Helvetica", 12))
        self.food_combo.pack(fill="x", pady=5)
        self.food_combo.bind('<KeyRelease>', self.update_food_suggestions)
        tk.Label(frame, text="Вес (грамм):", bg=BG_COLOR).pack(anchor="w")
        self.weight_entry = tk.Entry(frame, font=("Helvetica", 14), bg="white")
        self.weight_entry.pack(fill="x", pady=5, ipady=5)
        tk.Button(frame, text="Добавить в дневник", command=self.add_meal, bg=ACCENT_COLOR, fg="white", bd=0).pack(fill="x", pady=5, ipady=8)

        tk.Label(frame, text="Не нашли продукт? Добавьте свой (на 100 г):", bg=BG_COLOR, font=("Helvetica", 10, "italic")).pack(anchor="w", pady=(15,0))
        f_frame = tk.Frame(frame, bg=BG_COLOR)
        f_frame.pack(fill="x", pady=5)
        self.new_food_name = tk.Entry(f_frame, width=15, font=("Helvetica", 10)); self.new_food_name.insert(0, "Название"); self.new_food_name.pack(side="left", padx=2)
        self.new_food_cal = tk.Entry(f_frame, width=5, font=("Helvetica", 10)); self.new_food_cal.insert(0, "Ккал"); self.new_food_cal.pack(side="left", padx=2)
        self.new_food_prot = tk.Entry(f_frame, width=5, font=("Helvetica", 10)); self.new_food_prot.insert(0, "Б"); self.new_food_prot.pack(side="left", padx=2)
        self.new_food_fat = tk.Entry(f_frame, width=5, font=("Helvetica", 10)); self.new_food_fat.insert(0, "Ж"); self.new_food_fat.pack(side="left", padx=2)
        self.new_food_carb = tk.Entry(f_frame, width=5, font=("Helvetica", 10)); self.new_food_carb.insert(0, "У"); self.new_food_carb.pack(side="left", padx=2)
        tk.Button(frame, text="Сохранить свой продукт", command=self.add_custom_food, bg="gray", fg="white", bd=0).pack(fill="x", pady=5)

        self.nutrition_summary = tk.Label(frame, text="", bg=CARD_COLOR, font=("Helvetica", 12), justify="left", padx=10, pady=10)
        self.nutrition_summary.pack(fill="x", pady=10)
        self.update_nutrition_summary()

    def update_food_suggestions(self, event):
        query = self.food_combo.get()
        foods = logic.search_foods(query)
        self.food_combo['values'] = [f["name"] for f in foods]

    def add_meal(self):
        food_name = self.food_combo.get().strip()
        weight_str = self.weight_entry.get().strip()
        if not food_name or not weight_str:
            messagebox.showwarning("Внимание", "Введите продукт и вес.")
            return
        try:
            weight = float(weight_str)
            conn = db.get_connection()
            row = conn.execute("SELECT id, name FROM foods WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))", (food_name,)).fetchone()
            conn.close()
            if not row:
                messagebox.showerror("Ошибка", f"Продукт '{food_name}' не найден.")
                return
            logic.add_meal(self.current_user_id, row["id"], weight, "прием")
            self.update_nutrition_summary()
            messagebox.showinfo("Успех", f"'{row['name']}' ({weight} г) добавлено!")
            self.food_combo.set("")
            self.weight_entry.delete(0, tk.END)
            self.build_home_tab() 
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def add_custom_food(self):
        try:
            name = self.new_food_name.get().strip()
            if not name or name == "Название":
                messagebox.showwarning("Внимание", "Введите название продукта")
                return
            cal = float(self.new_food_cal.get() or 0)
            prot = float(self.new_food_prot.get() or 0)
            fat = float(self.new_food_fat.get() or 0)
            carb = float(self.new_food_carb.get() or 0)
            logic.add_food(name, cal, prot, fat, carb)
            self.update_food_suggestions(None)
            messagebox.showinfo("Успех", f"Продукт '{name}' добавлен в базу!")
            self.new_food_name.delete(0, tk.END); self.new_food_name.insert(0, "Название")
            self.new_food_cal.delete(0, tk.END); self.new_food_cal.insert(0, "Ккал")
            self.new_food_prot.delete(0, tk.END); self.new_food_prot.insert(0, "Б")
            self.new_food_fat.delete(0, tk.END); self.new_food_fat.insert(0, "Ж")
            self.new_food_carb.delete(0, tk.END); self.new_food_carb.insert(0, "У")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Проверьте данные: {str(e)}")

    def update_nutrition_summary(self):
        data = logic.get_day_nutrition(self.current_user_id)
        profile = logic.get_user_profile(self.current_user_id)
        norm = logic.calculate_norm(profile["weight"], profile["height"], profile["age"], profile["gender"], profile["activity_level"], profile["goal"])
        left = max(0, norm - data['cal'])
        text = f"🔥 Норма: {norm:.0f} ккал\n🍏 Съедено: {data['cal']:.0f} ккал\n✅ Осталось: {left:.0f} ккал\n\nБелки: {data['prot']:.1f} г\nЖиры: {data['fat']:.1f} г\nУглеводы: {data['carbs']:.1f} г"
        self.nutrition_summary.config(text=text)

    # --- ТРЕНИРОВКИ ---
    def build_workouts_tab(self):
        frame = tk.Frame(self.tab_workouts, bg=BG_COLOR, padx=15, pady=15)
        frame.pack(fill="both", expand=True)

        # Кнопка начала тренировки
        tk.Button(frame, text="▶ Начать тренировку по шаблону", command=self.start_workout, bg="green", fg="white", font=("Helvetica", 14, "bold"), bd=0).pack(fill="x", pady=10, ipady=10)

        # 1. Создание упражнения
        tk.Label(frame, text="1. Добавить новое упражнение:", bg=BG_COLOR, font=("Helvetica", 12, "bold")).pack(anchor="w")
        self.ex_name = tk.Entry(frame, font=("Helvetica", 14), bg="white")
        self.ex_name.pack(fill="x", pady=5, ipady=5)
        tk.Button(frame, text="Добавить в справочник", command=self.create_exercise, bg="gray", fg="white", bd=0).pack(fill="x", pady=5, ipady=5)

        # 2. Создание шаблона
        tk.Label(frame, text="2. Создать шаблон тренировки:", bg=BG_COLOR, font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(10,0))
        self.template_name = tk.Entry(frame, font=("Helvetica", 14), bg="white")
        self.template_name.pack(fill="x", pady=5, ipady=5)
        tk.Button(frame, text="Создать шаблон", command=self.create_template, bg=ACCENT_COLOR, fg="white", bd=0).pack(fill="x", pady=5, ipady=5)

        # 3. Добавление упражнения в шаблон
        tk.Label(frame, text="3. Добавить упражнение в шаблон:", bg=BG_COLOR, font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(10,0))
        tk.Label(frame, text="Выберите шаблон:", bg=BG_COLOR).pack(anchor="w")
        self.sel_template_combo = ttk.Combobox(frame, font=("Helvetica", 12), state="readonly")
        self.sel_template_combo.pack(fill="x", pady=2)

        tk.Label(frame, text="Выберите упражнение:", bg=BG_COLOR).pack(anchor="w")
        self.sel_ex_combo = ttk.Combobox(frame, font=("Helvetica", 12), state="readonly")
        self.sel_ex_combo.pack(fill="x", pady=2)

        p_frame = tk.Frame(frame, bg=BG_COLOR)
        p_frame.pack(fill="x", pady=5)
        tk.Label(p_frame, text="Подходы:", bg=BG_COLOR).pack(side="left")
        self.sets_entry = tk.Entry(p_frame, width=5, font=("Helvetica", 12)); self.sets_entry.insert(0, "3"); self.sets_entry.pack(side="left", padx=5)
        tk.Label(p_frame, text="Повторы:", bg=BG_COLOR).pack(side="left")
        self.reps_entry = tk.Entry(p_frame, width=5, font=("Helvetica", 12)); self.reps_entry.insert(0, "10"); self.reps_entry.pack(side="left", padx=5)
        tk.Label(p_frame, text="Вес(кг):", bg=BG_COLOR).pack(side="left")
        self.weight_entry_ex = tk.Entry(p_frame, width=5, font=("Helvetica", 12)); self.weight_entry_ex.pack(side="left", padx=5)
        tk.Button(frame, text="Добавить в выбранный шаблон", command=self.add_ex_to_template, bg=ACCENT_COLOR, fg="white", bd=0).pack(fill="x", pady=10, ipady=8)

        # 4. Расписание
        tk.Label(frame, text="4. Расписание:", bg=BG_COLOR, font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(10,0))
        self.schedule_combo = ttk.Combobox(frame, values=["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"], state="readonly")
        self.schedule_combo.pack(fill="x", pady=2)
        tk.Button(frame, text="Назначить выбранный шаблон на день", command=self.assign_schedule, bg=ACCENT_COLOR, fg="white", bd=0).pack(fill="x", pady=5, ipady=5)

        self.schedule_label = tk.Label(frame, text="", bg=BG_COLOR, justify="left")
        self.schedule_label.pack(anchor="w", pady=(10,0))

        self.refresh_all_combos()

    def refresh_all_combos(self):
        templates = logic.get_user_templates(self.current_user_id)
        self.sel_template_combo['values'] = [t["name"] for t in templates]
        exercises = logic.get_all_exercises()
        self.sel_ex_combo['values'] = [e["name"] for e in exercises]
        self.update_schedule_display()

    def create_exercise(self):
        try:
            logic.add_exercise(self.ex_name.get())
            self.ex_name.delete(0, tk.END)
            self.refresh_all_combos()
            messagebox.showinfo("Успех", "Упражнение добавлено!")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def create_template(self):
        try:
            logic.create_template(self.current_user_id, self.template_name.get())
            self.template_name.delete(0, tk.END)
            self.refresh_all_combos()
            messagebox.showinfo("Успех", "Шаблон создан!")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def add_ex_to_template(self):
        template_name = self.sel_template_combo.get()
        ex_name = self.sel_ex_combo.get()
        if not template_name or not ex_name:
            messagebox.showwarning("Внимание", "Выберите шаблон и упражнение из выпадающих списков!")
            return
        try:
            sets = int(self.sets_entry.get() or 3)
            reps = int(self.reps_entry.get() or 10)
            weight = float(self.weight_entry_ex.get() or 0)
            templates = logic.get_user_templates(self.current_user_id)
            template_id = next(t["id"] for t in templates if t["name"] == template_name)
            exercises = logic.get_all_exercises()
            ex_id = next(e["id"] for e in exercises if e["name"] == ex_name)
            logic.add_exercise_to_template(template_id, ex_id, sets, reps, weight)
            messagebox.showinfo("Успех", f"'{ex_name}' добавлено в '{template_name}'!")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def start_workout(self):
        template_name = self.sel_template_combo.get()
        if not template_name:
            messagebox.showwarning("Внимание", "Сначала выберите шаблон из выпадающего списка!")
            return
        templates = logic.get_user_templates(self.current_user_id)
        template_id = next(t["id"] for t in templates if t["name"] == template_name)
        exercises = logic.get_template_exercises(template_id)
        if not exercises:
            messagebox.showinfo("Инфо", "В этом шаблоне пока нет упражнений. Добавьте их сначала.")
            return
        self.show_workout_log(template_name, exercises)

    def show_workout_log(self, template_name, exercises):
        log_win = tk.Toplevel(self.root)
        log_win.title(f"Тренировка: {template_name}")
        log_win.geometry("450x600")
        log_win.configure(bg=BG_COLOR)

        tk.Label(log_win, text=f"Тренировка: {template_name}", font=("Helvetica", 16, "bold"), bg=BG_COLOR).pack(pady=15)

        canvas = tk.Canvas(log_win, bg=BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(log_win, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=BG_COLOR)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=420)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for ex in exercises:
            frame = tk.Frame(scroll_frame, bg=CARD_COLOR, pady=10, padx=10)
            frame.pack(fill="x", pady=5, padx=10)
            tk.Label(frame, text=ex["name"], font=("Helvetica", 12, "bold"), bg=CARD_COLOR).pack(anchor="w")
            
            p_frame = tk.Frame(frame, bg=CARD_COLOR)
            p_frame.pack(fill="x", pady=5)
            tk.Label(p_frame, text="Подходы:", bg=CARD_COLOR).pack(side="left")
            sets_entry = tk.Entry(p_frame, width=4); sets_entry.insert(0, str(ex["sets"] or 3)); sets_entry.pack(side="left", padx=2)
            tk.Label(p_frame, text="Повторы:", bg=CARD_COLOR).pack(side="left")
            reps_entry = tk.Entry(p_frame, width=4); reps_entry.insert(0, str(ex["reps"] or 10)); reps_entry.pack(side="left", padx=2)
            tk.Label(p_frame, text="Вес(кг):", bg=CARD_COLOR).pack(side="left")
            weight_entry = tk.Entry(p_frame, width=5); weight_entry.insert(0, str(ex["weight"] or 0)); weight_entry.pack(side="left", padx=2)

            ex_name_current = ex["name"]
            def save_result(name=ex_name_current, s=sets_entry, r=reps_entry, w=weight_entry):
                try:
                    sets = int(s.get()); reps = int(r.get()); weight = float(w.get())
                    ex_id = logic.get_exercise_id_by_name(name)
                    logic.save_workout_set(self.current_user_id, ex_id, sets, reps, weight)
                    messagebox.showinfo("Успех", f"Результат для '{name}' сохранен!")
                except Exception as e:
                    messagebox.showerror("Ошибка", str(e))

            tk.Button(frame, text="Сохранить результат", command=save_result, bg=ACCENT_COLOR, fg="white", bd=0).pack(fill="x", pady=5)

        tk.Button(log_win, text="Закрыть", command=log_win.destroy, bg="gray", fg="white", bd=0).pack(pady=20, ipady=5)

    def assign_schedule(self):
        template_name = self.sel_template_combo.get()
        if not template_name:
            messagebox.showwarning("Внимание", "Выберите шаблон из выпадающего списка!")
            return
        day_map = {"Понедельник": 1, "Вторник": 2, "Среда": 3, "Четверг": 4, "Пятница": 5, "Суббота": 6, "Воскресенье": 7}
        day = day_map.get(self.schedule_combo.get())
        if not day:
            messagebox.showwarning("Внимание", "Выберите день недели!")
            return
        templates = logic.get_user_templates(self.current_user_id)
        template_id = next(t["id"] for t in templates if t["name"] == template_name)
        logic.set_schedule_day(self.current_user_id, day, template_id)
        messagebox.showinfo("Успех", f"'{template_name}' назначено на {self.schedule_combo.get()}")
        self.update_schedule_display()

    def update_schedule_display(self):
        if not hasattr(self, 'schedule_label') or not self.schedule_label.winfo_exists():
            return 
        schedule = logic.get_schedule(self.current_user_id)
        day_names = {1: "Пн", 2: "Вт", 3: "Ср", 4: "Чт", 5: "Пт", 6: "Сб", 7: "Вс"}
        text = ""
        for day_num in range(1, 8):
            day_str = day_names.get(day_num, "?")
            if day_num in schedule:
                text += f"{day_str}: {schedule[day_num]}\n"
            else:
                text += f"{day_str}: —\n"
        self.schedule_label.config(text=text)

    # --- ПРОФИЛЬ ---
    def build_profile_tab(self):
        profile = logic.get_user_profile(self.current_user_id)
        frame = tk.Frame(self.tab_profile, bg=BG_COLOR, padx=15, pady=15)
        frame.pack(fill="both", expand=True)
        self.p_weight = self._add_input(frame, "Вес (кг):", profile.get("weight"))
        self.p_height = self._add_input(frame, "Рост (см):", profile.get("height"))
        self.p_age = self._add_input(frame, "Возраст:", profile.get("age"))
        tk.Button(frame, text="Сохранить профиль", command=self.save_profile, bg=ACCENT_COLOR, fg="white", bd=0, font=("Helvetica", 12, "bold")).pack(fill="x", pady=10, ipady=8)
        tk.Button(frame, text="Удалить аккаунт", command=self.delete_account, bg="white", fg="red", bd=1, relief="solid", font=("Helvetica", 12)).pack(fill="x", pady=10, ipady=8)

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

    def delete_account(self):
        if messagebox.askyesno("Удаление", "Вы уверены, что хотите удалить аккаунт?"):
            try:
                logic.delete_user(self.current_user_id)
                messagebox.showinfo("Удалено", "Аккаунт удален.")
                self.show_welcome_screen()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = FitnessApp(root)
    root.mainloop()