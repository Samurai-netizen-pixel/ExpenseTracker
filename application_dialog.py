import tkinter as tk
from tkinter import ttk, messagebox

from expense import Expense


class ApplicationDialog(tk.Toplevel):
    def __init__(self, parent, on_save, existing_expense: Expense = None):
        super().__init__(parent)
        self.transient(parent)
        self.title("Добавить/Редактировать расход")
        self.__parent = parent
        self.__on_save = on_save
        self.__existing_expense = existing_expense

        self.__category = tk.StringVar()
        self.__amount = tk.DoubleVar()
        self.__description = tk.StringVar()

        self._create_widgets()
        self._load_existing_data()

    def _create_widgets(self):
        self.__main_frame = ttk.Frame(self, padding="10")
        self.__main_frame.grid(row=0, column=0)

        ttk.Label(self.__main_frame, text="Категория:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.__category_entry = ttk.Entry(self.__main_frame, textvariable=self.__category, width=30)
        self.__category_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(self.__main_frame, text="Сумма:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.__amount_entry = ttk.Entry(self.__main_frame, textvariable=self.__amount, width=30)
        self.__amount_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(self.__main_frame, text="Описание:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.__description_entry = ttk.Entry(self.__main_frame, textvariable=self.__description, width=30)
        self.__description_entry.grid(row=2, column=1, pady=5, padx=5)

        self.__save_button = ttk.Button(self.__main_frame, text="Сохранить", command=self._save_expense)
        self.__save_button.grid(row=3, column=0, pady=10, padx=5)

        self.__cancel_button = ttk.Button(self.__main_frame, text="Отмена", command=self.destroy)
        self.__cancel_button.grid(row=3, column=1, pady=10, padx=5)

        self.__category_entry.focus_set()

    def _load_existing_data(self):
        if self.__existing_expense:
            self.__category.set(self.__existing_expense.get_category())
            self.__amount.set(self.__existing_expense.__int__())
            self.__description.set(self.__existing_expense.get_description())

    def _save_expense(self):
        category = self.__category.get().strip()

        try:
            amount_value = self.__amount.get()
        except tk.TclError:
            amount_value = None

        description = self.__description.get().strip()

        if not category:
            messagebox.showwarning("Внимание", "Пожалуйста, введите категорию расхода.")
            return

        if not amount_value or not isinstance(amount_value, (int, float)) or amount_value <= 0:
            messagebox.showwarning("Внимание", "Пожалуйста, введите корректную положительную сумму.")
            return

        self.__on_save(category, amount_value, description)
        self.destroy()
