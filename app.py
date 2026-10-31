import tkinter as tk
from tkinter import ttk, messagebox
import logic
import db

BG_COLOR = "#F2F2F7"
CARD_COLOR = "#FFFFFF"
ACCENT_COLOR = "#007AFF"
GRAY_TEXT = "#8E8E93"

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
        # expand=True и fill="both" заставляют фрейм растянуться на всё окно
        frame.pack(expand=True, fill="both", padx=30)

        # Создаем внутренний фрейм для центрирования
        center_frame = tk.Frame(frame, bg=BG_COLOR)
        center_frame.pack(expand=True) # expand=True центрирует этот блок по вертикали

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

    def create_card(self, parent, title, text):
        card = tk.Frame(parent, bg=CARD_COLOR, bd=0)
        card.pack(fill="x", pady=5, padx=15)
        tk.Label(card, text=title, font=("Helvetica", 14, "bold"), bg=CARD_COLOR).pack(anchor="w", padx=15, pady=(10, 0))
        tk.Label(card, text=text, font=("Helvetica", 12), bg=CARD_COLOR, fg="gray", justify="left").pack(anchor="w", padx=15, pady=(0, 10))

    def build_home_tab(self):
        # Очищаем старые карточки
        for widget in self.tab_home.winfo_children():
            widget.destroy()

        scroll = tk.Frame(self.tab_home, bg=BG_COLOR)
        scroll.pack(fill="both", expand=True, pady=10)
        
        # ... и дальше весь остальной код ...

        profile = logic.get_user_profile(self.current_user_id)
        self.norm_cal = logic.calculate_norm(profile["weight"], profile["height"], profile["age"], profile["gender"], profile["activity_level"], profile["goal"])
        today = logic.get_day_nutrition(self.current_user_id)
        
        # --- КАРТОЧКА КАЛОРИЙ ---
        left_cal = max(0, self.norm_cal - today['cal'])
        cal_text = f"Норма: {self.norm_cal:.0f} ккал\nСъедено: {today['cal']:.0f} ккал\nОсталось: {left_cal:.0f} ккал"
        self.create_card(scroll, "🔥 Калории", cal_text)

        # --- КАРТОЧКА БЖУ (УМНЫЙ РАСЧЕТ) ---
        n_prot, n_fat, n_carb = self.calculate_macros(self.norm_cal, profile["goal"])
        
        # Создаем карточку БЖУ вручную, чтобы покрасить цифры
        card = tk.Frame(scroll, bg=CARD_COLOR, bd=0)
        card.pack(fill="x", pady=5, padx=15)
        tk.Label(card, text="🥩 БЖУ", font=("Helvetica", 14, "bold"), bg=CARD_COLOR).pack(anchor="w", padx=15, pady=(10, 5))
        
        # Белки
        prot_color = "red" if today['prot'] > n_prot else "green"
        tk.Label(card, text=f"Белки: {today['prot']:.1f} / {n_prot:.1f} г", bg=CARD_COLOR, fg=prot_color).pack(anchor="w", padx=15)
        
        # Жиры
        fat_color = "red" if today['fat'] > n_fat else "green"
        tk.Label(card, text=f"Жиры: {today['fat']:.1f} / {n_fat:.1f} г", bg=CARD_COLOR, fg=fat_color).pack(anchor="w", padx=15)
        
        # Углеводы
        carb_color = "red" if today['carbs'] > n_carb else "green"
        tk.Label(card, text=f"Углеводы: {today['carbs']:.1f} / {n_carb:.1f} г", bg=CARD_COLOR, fg=carb_color).pack(anchor="w", padx=15, pady=(0, 10))

        # --- ТРЕНИРОВКА / СОВЕТ ---
        schedule = logic.get_schedule(self.current_user_id)
        today_weekday = 1 
        if today_weekday in schedule:
            self.create_card(scroll, "🏋️ Тренировка сегодня", schedule[today_weekday])
        else:
            self.create_card(scroll, "💡 Совет дня", "Сегодня тренировки нет. Отдыхайте!")

    def calculate_macros(self, calories, goal):
        """Умный расчет БЖУ в зависимости от цели."""
        # По умолчанию (поддержание): 30% белки, 30% жиры, 40% углеводы
        if goal == "похудение":
            # Больше белка (40%), меньше жиров (20%), углеводы (40%)
            p, f, c = 0.40, 0.20, 0.40
        elif goal == "набор массы":
            # Белки (25%), жиры (25%), углеводы (50%)
            p, f, c = 0.25, 0.25, 0.50
        else:
            # Поддержание
            p, f, c = 0.30, 0.30, 0.40
        
        # 1 г белка = 4 ккал, 1 г жира = 9 ккал, 1 г углеводов = 4 ккал
        n_prot = (calories * p) / 4
        n_fat = (calories * f) / 9
        n_carb = (calories * c) / 4
        return n_prot, n_fat, n_carb

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
        tk.Button(frame, text="Добавить в дневник", command=self.add_meal, bg=ACCENT_COLOR, fg="white", bd=0).pack(fill="x", pady=10, ipady=8)
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

    def update_nutrition_summary(self):
        data = logic.get_day_nutrition(self.current_user_id)
        profile = logic.get_user_profile(self.current_user_id)
        norm = logic.calculate_norm(profile["weight"], profile["height"], profile["age"], profile["gender"], profile["activity_level"], profile["goal"])
        left = max(0, norm - data['cal'])
        text = f"🔥 Норма: {norm:.0f} ккал\n🍏 Съедено: {data['cal']:.0f} ккал\n✅ Осталось: {left:.0f} ккал\n\nБелки: {data['prot']:.1f} г\nЖиры: {data['fat']:.1f} г\nУглеводы: {data['carbs']:.1f} г"
        self.nutrition_summary.config(text=text)

    # --- ВКЛАДКА ТРЕНИРОВОК (ИСПРАВЛЕНО) ---
    def build_workouts_tab(self):
        frame = tk.Frame(self.tab_workouts, bg=BG_COLOR, padx=15, pady=15)
        frame.pack(fill="both", expand=True)
        
        # Создание шаблона
        tk.Label(frame, text="Название новой тренировки:", bg=BG_COLOR).pack(anchor="w")
        self.template_name = tk.Entry(frame, font=("Helvetica", 14), bg="white")
        self.template_name.pack(fill="x", pady=5, ipady=5)
        tk.Button(frame, text="Создать шаблон", command=self.create_template, bg=ACCENT_COLOR, fg="white", bd=0).pack(fill="x", pady=5, ipady=5)

        # Список шаблонов
        tk.Label(frame, text="Мои шаблоны (выбери и назначь на день):", bg=BG_COLOR, font=("Helvetica", 12)).pack(anchor="w", pady=(15,0))
        self.templates_listbox = tk.Listbox(frame, font=("Helvetica", 12), bg="white", bd=0, height=6)
        self.templates_listbox.pack(fill="x", pady=5)
        
        # Назначение на день
        tk.Label(frame, text="Выбери день недели для назначения:", bg=BG_COLOR).pack(anchor="w", pady=(10,0))
        self.schedule_combo = ttk.Combobox(frame, values=["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"], state="readonly")
        self.schedule_combo.pack(fill="x", pady=2)
        tk.Button(frame, text="Назначить выбранный шаблон", command=self.assign_schedule, bg=ACCENT_COLOR, fg="white", bd=0).pack(fill="x", pady=5, ipady=5)

        # Текущее расписание
        tk.Label(frame, text="Текущее расписание:", bg=BG_COLOR, font=("Helvetica", 12)).pack(anchor="w", pady=(15,0))
        self.schedule_label = tk.Label(frame, text="", bg=BG_COLOR, justify="left")
        self.schedule_label.pack(anchor="w")
        
        self.refresh_templates()
        self.update_schedule_display()

    def create_template(self):
        try:
            logic.create_template(self.current_user_id, self.template_name.get())
            self.refresh_templates()
            self.template_name.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def assign_schedule(self):
        # Получаем выбранный шаблон
        sel = self.templates_listbox.curselection()
        if not sel:
            messagebox.showwarning("Внимание", "Сначала выберите шаблон из списка!")
            return
        
        # Получаем выбранный день
        day_name = self.schedule_combo.get()
        if not day_name:
            messagebox.showwarning("Внимание", "Выберите день недели!")
            return

        day_map = {"Понедельник": 1, "Вторник": 2, "Среда": 3, "Четверг": 4, "Пятница": 5, "Суббота": 6, "Воскресенье": 7}
        day_num = day_map[day_name]
        
        template_name = self.templates_listbox.get(sel[0])
        templates = logic.get_user_templates(self.current_user_id)
        template_id = next(t["id"] for t in templates if t["name"] == template_name)
        
        # Назначаем
        logic.set_schedule_day(self.current_user_id, day_num, template_id)
        messagebox.showinfo("Успех", f"'{template_name}' назначено на {day_name}")
        self.update_schedule_display()

    def update_schedule_display(self):
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

    def refresh_templates(self):
        self.templates_listbox.delete(0, tk.END)
        for t in logic.get_user_templates(self.current_user_id):
            self.templates_listbox.insert(tk.END, t["name"])

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