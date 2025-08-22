import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from application_dialog import ApplicationDialog
from application_view_model import ApplicationViewModel


def format_currency(amount: int | float):
    return f"{amount:,.2f}".replace(',', ' ')


def is_float(value: str):
    try:
        float(value)
        return True
    except ValueError:
        return False


class ApplicationView(tk.Tk):
    def __init__(self, viewmodel: ApplicationViewModel):
        super().__init__()
        self.__viewmodel = viewmodel
        self.__viewmodel.on_data_changed = self._update_display

        self.title("Трекер Расходов (Без сохранения)")
        self.geometry("1200x1200")

        self._create_widgets()
        self._update_display()

    def _create_widgets(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        self.__file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=self.__file_menu)
        self.__file_menu.add_command(label="Установить бюджет", command=self._open_budget_dialog)
        self.__file_menu.add_separator()
        self.__file_menu.add_command(label="Выход", command=self.quit)

        self.__main_frame = ttk.Frame(self, padding="10")
        self.__main_frame.pack(fill=tk.BOTH, expand=True)

        self.__stats_frame = ttk.LabelFrame(self.__main_frame, text="Общая статистика", padding="10")
        self.__stats_frame.grid(row=0, column=0, columnspan=2, pady=10)

        self.__total_expenses_label = ttk.Label(self.__stats_frame, text="Общие расходы: -")
        self.__total_expenses_label.grid(row=0, column=0, sticky=tk.W, padx=5)

        self.__budget_summary_label = ttk.Label(self.__stats_frame, text="Бюджеты: -")
        self.__budget_summary_label.grid(row=1, column=0, sticky=tk.W, padx=5)

        self.__expense_tabs = ttk.Notebook(self.__main_frame)
        self.__expense_tabs.grid(row=1, column=0, sticky=tk.W, padx=5)

        expense_tab_names = ["Все расходы", "Добавить расход", "Удалить или редактировать расходы"]
        expense_tab_frames = [ttk.Frame(self.__expense_tabs) for _ in range(len(expense_tab_names))]

        for frame, name in zip(expense_tab_frames, expense_tab_names):
            self.__expense_tabs.add(frame, text=name)

        self._setup_expense_table(expense_tab_frames[0])
        self._setup_add_expense_form(expense_tab_frames[1])
        self._setup_delete_expense_form(expense_tab_frames[2])

        self.__budget_tabs = ttk.Notebook(self.__main_frame)
        self.__budget_tabs.grid(row=2, column=0, sticky=tk.W, padx=5)

        budget_tab_names = ["Все бюджеты", "Добавить бюджет"]
        budget_tab_frames = [ttk.Frame(self.__budget_tabs) for _ in range(len(budget_tab_names))]

        for frame, name in zip(budget_tab_frames, budget_tab_names):
            self.__budget_tabs.add(frame, text=name)

        self._setup_budget_table(budget_tab_frames[0])
        self._setup_add_budget_form(budget_tab_frames[1])

        self.__reports_frame = ttk.LabelFrame(self.__main_frame, text="Отчеты", padding="10")
        self.__reports_frame.grid(row=2, column=1, pady=10)

        self.__generate_report_button = ttk.Button(self.__reports_frame, text="Сгенерировать отчет",
                                                   command=self._generate_report)
        self.__generate_report_button.pack(pady=5)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=3)
        self.grid_rowconfigure(2, weight=1)

    def _setup_expense_table(self, frame):
        columns = ('Категория', 'Сумма', 'Дата', 'Описание')
        self.__expense_tree = ttk.Treeview(frame, columns=columns, show='headings')

        for col in columns:
            self.__expense_tree.heading(col, text=col)
            self.__expense_tree.column(col, minwidth=0, width=100)

        self.__expense_tree.grid(row=0, column=0)
        frame.columnconfigure(0, weight=1)

    def _setup_budget_table(self, frame):
        columns = ('Категория', 'Потрачено', 'Общая сумма', 'Остаток')
        self.__budget_tree = ttk.Treeview(frame, columns=columns, show='headings')

        for col in columns:
            self.__budget_tree.heading(col, text=col)
            self.__budget_tree.column(col, minwidth=0, width=100)

        self.__budget_tree.grid(row=0, column=0)
        frame.columnconfigure(0, weight=1)

    def _setup_add_expense_form(self, frame):
        field_width = 16

        ttk.Label(frame, text="Категория:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.__expense_category_entry = ttk.Entry(frame, width=field_width)
        self.__expense_category_entry.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)

        ttk.Label(frame, text="Сумма:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.__expense_amount_entry = ttk.Entry(frame, width=field_width)
        self.__expense_amount_entry.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)

        ttk.Label(frame, text="Описание:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)
        self.__expense_description_entry = tk.Entry(frame, width=field_width)
        self.__expense_description_entry.grid(row=3, column=1, sticky=tk.W, padx=10, pady=10)

        self.__add_button = ttk.Button(frame, text="Добавить", command=self.add_expense)
        self.__add_button.grid(row=4, columnspan=2, pady=10)

    def add_expense(self):
        amount = self.__expense_amount_entry.get().strip()
        category = self.__expense_category_entry.get()
        description = self.__expense_description_entry.get().strip()

        try:
            if not (amount and category):
                raise ValueError("Все поля кроме описания - обязательны!")

            amount = float(amount)

            self.__viewmodel.add_expense(category, amount, description)
            messagebox.showinfo("Успешно", "Расход успешно добавлен!")
            self.clear_expense_entries()
        except ValueError as ve:
            messagebox.showerror("Ошибка", str(ve))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при добавлении расхода: {e}")

    def _setup_add_budget_form(self, frame):
        field_width = 16

        ttk.Label(frame, text="Категория:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.__budget_category_entry = ttk.Entry(frame, width=field_width)
        self.__budget_category_entry.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)

        ttk.Label(frame, text="Сумма:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.__budget_amount_entry = ttk.Entry(frame, width=field_width)
        self.__budget_amount_entry.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)

        self.__add_button = ttk.Button(frame, text="Добавить", command=self.add_budget)
        self.__add_button.grid(row=4, columnspan=2, pady=10)

    def add_budget(self):
        confirm = messagebox.askyesno("Подтверждение",
                                      "Вы уверены, что хотите добавить это бюджет?\nПосле добавления его нельзя будет изменить!")

        if confirm:
            amount = self.__budget_amount_entry.get().strip()
            category = self.__budget_category_entry.get()

            try:
                if not (amount and category):
                    raise ValueError("Все поля обязательны!")

                amount = float(amount)
                spent_amount = sum(expense.__int__() for expense in self.__viewmodel.get_expenses_by_category(category))
                remaining = amount - spent_amount

                if remaining >= 0:
                    status = f"Осталось: {format_currency(remaining)}"
                else:
                    status = f"Превышен на: {format_currency(-remaining)}"
                success, message = self.__viewmodel.add_budget(category, amount, spent_amount, status)

                if not success:
                    messagebox.showerror("Ошибка", message)

                self.__viewmodel.add_budget(category, amount, spent_amount, status)
                messagebox.showinfo("Успешно", "Бюджет успешно добавлен!")
                self.clear_budget_entries()
            except ValueError as ve:
                messagebox.showerror("Ошибка", str(ve))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при добавлении бюджета: {e}")

    def _setup_delete_expense_form(self, frame):
        self.__expenses_frame = ttk.LabelFrame(frame, text="Расходы", padding="10")
        self.__expenses_frame.grid(row=1, column=0, padx=5)

        self.__expenses_listbox = tk.Listbox(self.__expenses_frame, width=50, height=15, font=("Arial", 10))
        self.__expenses_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.__scrollbar = ttk.Scrollbar(self.__expenses_frame, orient=tk.VERTICAL,
                                         command=self.__expenses_listbox.yview)
        self.__scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.__expenses_listbox.config(yscrollcommand=self.__scrollbar.set)

        self.__expense_actions_frame = ttk.Frame(frame, padding="5")
        self.__expense_actions_frame.grid(row=1, column=1, pady=10)

        self.__edit_expense_button = ttk.Button(self.__expense_actions_frame, text="Редактировать",
                                                command=self._open_edit_expense_dialog)
        self.__edit_expense_button.pack(pady=5)

        self.__delete_expense_button = ttk.Button(self.__expense_actions_frame, text="Удалить",
                                                  command=self._delete_selected_expense)
        self.__delete_expense_button.pack(pady=5)

    def _open_edit_expense_dialog(self):
        selected_indices = self.__expenses_listbox.curselection()

        if not selected_indices:
            messagebox.showwarning("Внимание", "Выберите расход для редактирования.")
            return

        try:
            selected_expense = self.__current_expenses_display_data[selected_indices[0]]
            dialog = ApplicationDialog(self, self._on_expense_saved, existing_expense=selected_expense)
            self.wait_window(dialog)
            self.__viewmodel.delete_expense(selected_expense)

        except IndexError:
            messagebox.showerror("Ошибка", "Не удалось получить данные выбранного расхода.")

    def _delete_selected_expense(self):
        selected_indices = self.__expenses_listbox.curselection()

        if not selected_indices:
            messagebox.showwarning("Внимание", "Выберите расход для удаления.")
            return

        confirm = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот расход?")

        if confirm:
            try:
                expense_to_delete = self.__current_expenses_display_data[selected_indices[0]]
                success, message = self.__viewmodel.delete_expense(expense_to_delete)

                if success:
                    messagebox.showinfo("Успех", message)
                else:
                    messagebox.showerror("Ошибка", message)
            except IndexError:
                messagebox.showerror("Ошибка", "Не удалось удалить расход. Попробуйте еще раз.")

    def _update_display(self):
        self.__expenses_listbox.delete(0, tk.END)
        self.clear_expense_tree()
        self.clear_budget_tree()

        expenses = self.__viewmodel.get_all_expenses()
        self.__current_expenses_display_data = []

        for expense in expenses:
            self.__expense_tree.insert("", tk.END, values=expense)
            self.__expenses_listbox.insert(tk.END, expense)
            self.__current_expenses_display_data.append(expense)
            print(self.__current_expenses_display_data)

        for category in self.__viewmodel.get_all_categories():
            spent, budget_amount, status = self.__viewmodel.get_budget_status(category)
            budget = self.__viewmodel.add_and_get_budget_without_update(category, budget_amount, spent, status)
            self.__budget_tree.insert("", tk.END, values=budget)

        self.__total_expenses_label.config(
            text=f"Общие расходы: {format_currency(self.__viewmodel.get_total_expenses())}")

        if self.__viewmodel.get_all_categories:
            total_budgeted = sum(budget.get_amount() for budget in self.__viewmodel.get_budgets())
            self.__budget_summary_label.config(text=f"Общие бюджеты: {format_currency(total_budgeted)}")
        else:
            self.__budget_summary_label.config(text="Бюджеты: Не установлены")

    def _on_expense_saved(self, category: str, amount: int | float, description: str):
        success, message = self.__viewmodel.add_expense(category, amount, description)

        if not success:
            messagebox.showerror("Ошибка", message)

    def _open_budget_dialog(self):
        category = simpledialog.askstring("Установка бюджета", "Введите категорию для бюджета:", parent=self)

        if category:
            amount_str = simpledialog.askstring("Установка бюджета", f"Введите сумму бюджета для '{category}':",
                                                parent=self)
            if amount_str and is_float(amount_str):
                amount = float(amount_str)
                spent_amount = sum(expense.__int__() for expense in self.__viewmodel.get_expenses_by_category(category))
                remaining = amount - spent_amount

                if remaining >= 0:
                    status = f"Осталось: {format_currency(remaining)}"
                else:
                    status = f"Превышен на: {format_currency(-remaining)}"
                success, message = self.__viewmodel.add_budget(category, amount, spent_amount, status)

                if not success:
                    messagebox.showerror("Ошибка", message)
            else:
                messagebox.showwarning("Внимание", "Пожалуйста, введите корректную сумму.")
        else:
            messagebox.showwarning("Внимание", "Пожалуйста, введите категорию бюджета.")

    def _generate_report(self):
        messagebox.showinfo("Отчеты", "Функция генерации отчетов пока не реализована.")

    def clear_expense_tree(self):
        for item in self.__expense_tree.get_children():
            self.__expense_tree.delete(item)

    def clear_budget_tree(self):
        for item in self.__budget_tree.get_children():
            self.__budget_tree.delete(item)

    def clear_expense_entries(self):
        self.__expense_amount_entry.delete(0, tk.END)
        self.__expense_category_entry.delete(0, tk.END)
        self.__expense_description_entry.delete(0, tk.END)

    def clear_budget_entries(self):
        self.__budget_amount_entry.delete(0, tk.END)
        self.__budget_category_entry.delete(0, tk.END)
