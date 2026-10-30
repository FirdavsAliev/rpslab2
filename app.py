import tkinter as tk
from tkinter import ttk, messagebox
import logic
import db

class FitnessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fitness Tracker - Личный помощник")
        self.root.geometry("800x600")
        self.current_user_id = None
        self.current_username = ""
        
        # Инициализация БД при запуске
        db.init_db()
        
        self.show_login_screen()

    def show_login_screen(self):
        self.clear_window()
        
        frame = ttk.Frame(self.root, padding=40)
        frame.pack(expand=True)
        
        ttk.Label(frame, text="Вход в Fitness Tracker", font=("Arial", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=20)
        
        ttk.Label(frame, text="Логин:").grid(row=1, column=0, sticky="w", pady=5)
        self.login_entry = ttk.Entry(frame, width=30)
        self.login_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Пароль:").grid(row=2, column=0, sticky="w", pady=5)
        self.pass_entry = ttk.Entry(frame, show="*", width=30)
        self.pass_entry.grid(row=2, column=1, pady=5)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Войти", command=self.do_login).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Регистрация", command=self.do_register).pack(side="left", padx=5)

    def do_login(self):
        try:
            user_id = logic.login_user(self.login_entry.get(), self.pass_entry.get())
            self.current_user_id = user_id
            self.current_username = self.login_entry.get()
            self.show_main_screen()
        except Exception as e:
            messagebox.showerror("Ошибка входа", str(e))

    def do_register(self):
        try:
            logic.register_user(self.login_entry.get(), self.pass_entry.get())
            messagebox.showinfo("Успех", "Регистрация прошла успешно! Теперь войдите.")
        except Exception as e:
            messagebox.showerror("Ошибка регистрации", str(e))

    def show_main_screen(self):
        self.clear_window()
        
        # Верхняя панель
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill="x")
        ttk.Label(top_frame, text=f"Пользователь: {self.current_username}", font=("Arial", 12, "bold")).pack(side="left")
        ttk.Button(top_frame, text="Выйти", command=self.show_login_screen).pack(side="right")
        
        # Вкладки
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_nutrition = ttk.Frame(notebook)
        self.tab_workouts = ttk.Frame(notebook)
        self.tab_analytics = ttk.Frame(notebook)
        
        notebook.add(self.tab_nutrition, text="🍎 Питание")
        notebook.add(self.tab_workouts, text="🏋️ Тренировки")
        notebook.add(self.tab_analytics, text="📊 Аналитика")
        
        self.build_nutrition_tab()
        self.build_workouts_tab()
        self.build_analytics_tab()
        
        # Статус-бар (эвристика "Видимость статуса")
        self.status_var = tk.StringVar(value="Готово к работе")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x")

    def build_nutrition_tab(self):
        f = self.tab_nutrition
        
        # Форма добавления еды
        form = ttk.LabelFrame(f, text="Добавить прием пищи", padding=10)
        form.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(form, text="Продукт:").grid(row=0, column=0)
        self.food_combo = ttk.Combobox(form, width=25)
        self.food_combo.grid(row=0, column=1, padx=5)
        self.food_combo['values'] = [f["name"] for f in logic.get_all_foods()]
        
        ttk.Label(form, text="Вес (г):").grid(row=0, column=2)
        self.weight_entry = ttk.Entry(form, width=10)
        self.weight_entry.grid(row=0, column=3, padx=5)
        
        ttk.Button(form, text="Добавить", command=self.add_meal).grid(row=0, column=4, padx=5)
        
        # Сводка за день
        self.summary_label = ttk.Label(f, text="", font=("Arial", 12))
        self.summary_label.pack(pady=20)
        self.update_nutrition_summary()

    def add_meal(self):
        food_name = self.food_combo.get()
        weight = self.weight_entry.get()
        
        if not food_name or not weight:
            messagebox.showwarning("Внимание", "Выберите продукт и укажите вес")
            return
            
        try:
            weight = float(weight)
            foods = logic.get_all_foods()
            food_id = next(f["id"] for f in foods if f["name"] == food_name)
            logic.add_meal(self.current_user_id, food_id, weight, "прием")
            self.update_nutrition_summary()
            self.status_var.set(f"Добавлено: {food_name} ({weight} г)")
            self.weight_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def update_nutrition_summary(self):
        data = logic.get_day_nutrition(self.current_user_id)
        text = f"Съедено сегодня:\nКалории: {data['cal']:.1f} ккал\nБелки: {data['prot']:.1f} г\nЖиры: {data['fat']:.1f} г\nУглеводы: {data['carbs']:.1f} г"
        self.summary_label.config(text=text)

    def build_workouts_tab(self):
        f = self.tab_workouts
        ttk.Label(f, text="Планировщик тренировок", font=("Arial", 14)).pack(pady=10)
        
        # Рекомендации
        recs = logic.get_recommendations(self.current_user_id)
        rec_text = "\n".join([f"• {r}" for r in recs])
        
        rec_frame = ttk.LabelFrame(f, text="Рекомендации системы", padding=10)
        rec_frame.pack(fill="x", padx=10, pady=10)
        ttk.Label(rec_frame, text=rec_text, foreground="blue").pack()

    def build_analytics_tab(self):
        f = self.tab_analytics
        ttk.Label(f, text="Аналитика прогресса", font=("Arial", 14)).pack(pady=10)
        
        # Простой текстовый отчет
        data = logic.get_day_nutrition(self.current_user_id)
        report = f"Ваш отчет за сегодня:\n\nКалории: {data['cal']:.1f}\nБелки: {data['prot']:.1f}\nЖиры: {data['fat']:.1f}\nУглеводы: {data['carbs']:.1f}"
        
        ttk.Label(f, text=report, justify="left").pack(pady=20)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FitnessApp(root)
    root.mainloop()