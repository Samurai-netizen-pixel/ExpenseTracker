import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from expense_entry_dialog import ExpenseEntryDialog
from expense_view_model import ExpenseViewModel


def format_currency(amount: int | float):
    return f"{amount:,.2f}".replace(',', ' ')


def is_float(value: str):
    try:
        float(value)
        return True
    except ValueError:
        return False


class MainWindow(tk.Tk):
    def __init__(self, viewmodel: ExpenseViewModel):
        super().__init__()
        self.__viewmodel = viewmodel
        self.__viewmodel.on_data_changed = self._update_display

        self.title("Трекер Расходов (Без сохранения)")
        self.geometry("800x600")

        self._create_widgets()
        self._update_display()

    def _create_widgets(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        self.__file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=self.__file_menu)
        self.__file_menu.add_command(label="Добавить расход", command=self._open_add_expense_dialog)
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

        self.__expenses_frame = ttk.LabelFrame(self.__main_frame, text="Расходы", padding="10")
        self.__expenses_frame.grid(row=1, column=0, padx=5)

        self.__expenses_listbox = tk.Listbox(self.__expenses_frame, width=50, height=15, font=("Arial", 10))
        self.__expenses_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.__scrollbar = ttk.Scrollbar(self.__expenses_frame, orient=tk.VERTICAL,
                                         command=self.__expenses_listbox.yview)
        self.__scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.__expenses_listbox.config(yscrollcommand=self.__scrollbar.set)

        self.__expense_actions_frame = ttk.Frame(self.__main_frame, padding="5")
        self.__expense_actions_frame.grid(row=1, column=1, pady=10)

        self.__add_expense_button_toolbar = ttk.Button(self.__expense_actions_frame, text="Добавить",
                                                       command=self._open_add_expense_dialog)
        self.__add_expense_button_toolbar.pack(pady=5)
        self.__edit_expense_button = ttk.Button(self.__expense_actions_frame, text="Редактировать",
                                                command=self._open_edit_expense_dialog)
        self.__edit_expense_button.pack(pady=5)
        self.__delete_expense_button = ttk.Button(self.__expense_actions_frame, text="Удалить",

                                                  command=self._delete_selected_expense)
        self.__delete_expense_button.pack(pady=5)

        self.__budgets_frame = ttk.LabelFrame(self.__main_frame, text="Бюджеты", padding="10")
        self.__budgets_frame.grid(row=2, column=0, pady=10)

        self.__budgets_listbox = tk.Listbox(self.__budgets_frame, width=50, height=5, font=("Arial", 10))
        self.__budgets_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.__budgets_scrollbar = ttk.Scrollbar(self.__budgets_frame, orient=tk.VERTICAL,
                                                 command=self.__budgets_listbox.yview)
        self.__budgets_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.__budgets_listbox.config(yscrollcommand=self.__budgets_scrollbar.set)

        self.__reports_frame = ttk.LabelFrame(self.__main_frame, text="Отчеты", padding="10")
        self.__reports_frame.grid(row=2, column=1, pady=10)

        self.__generate_report_button = ttk.Button(self.__reports_frame, text="Сгенерировать отчет",
                                                   command=self._generate_report)
        self.__generate_report_button.pack(pady=5)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=3)
        self.grid_rowconfigure(2, weight=1)

    def _update_display(self):
        self.__expenses_listbox.delete(0, tk.END)
        self.__budgets_listbox.delete(0, tk.END)

        self.__current_expenses_display_data = []

        for expense in self.__viewmodel.get_all_expenses():
            self.__expenses_listbox.insert(tk.END, str(expense))
            self.__current_expenses_display_data.append(expense)

        for category in self.__viewmodel.get_all_categories():
            spent, budget_amount, status = self.__viewmodel.get_budget_status(category)
            budget = self.__viewmodel.add_and_get_budget_without_update(category, budget_amount, spent, status)

            if budget_amount != 0:
                self.__budgets_listbox.insert(tk.END, budget.__str__())
            else:
                self.__budgets_listbox.insert(tk.END, f"{category}: {format_currency(spent)} (Нет бюджета)")

        self.__total_expenses_label.config(
            text=f"Общие расходы: {format_currency(self.__viewmodel.get_total_expenses())}")

        if self.__viewmodel.get_all_categories:
            total_budgeted = sum(budget.__int__() for budget in self.__viewmodel.get_budgets())
            self.__budget_summary_label.config(text=f"Общие бюджеты: {format_currency(total_budgeted)}")
        else:
            self.__budget_summary_label.config(text="Бюджеты: Не установлены")

    def _open_add_expense_dialog(self):
        dialog = ExpenseEntryDialog(self, self._on_expense_saved)
        self.wait_window(dialog)

    def _open_edit_expense_dialog(self):
        selected_indices = self.__expenses_listbox.curselection()

        if not selected_indices:
            messagebox.showwarning("Внимание", "Выберите расход для редактирования.")
            return

        try:
            selected_expense = self.__current_expenses_display_data[selected_indices[0]]
            dialog = ExpenseEntryDialog(self, self._on_expense_saved, existing_expense=selected_expense)
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
