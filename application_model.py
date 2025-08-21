import json

from budget import Budget
from expense import Expense

DATA_FILE = "expenses_data.json"


class ApplicationModel:
    def __init__(self):
        self.__expenses = []
        self.__budgets = {}
        self._load_data()

    def add_expense(self, expense: Expense):
        self.__expenses.append(expense)
        self._save_data()

    def get_expenses(self):
        return self.__expenses

    def add_budget(self, budget: Budget):
        self.__budgets[budget.get_category()] = budget
        self._save_data()

    def get_budget(self, category: str):
        return self.__budgets.get(category)

    def get_all_budgets(self):
        return list(self.__budgets.values())

    def delete_expense(self, expense: Expense):
        self.__expenses.remove(expense)
        self._save_data()

    def _save_data(self):
        data = {
            "expenses": [{"category": expense.get_category(), "amount": expense.__int__(),
                          "description": expense.get_description()} for expense in
                         self.__expenses],
            "budgets": {category: {"spent amount": budget.get_spent_amount(), "amount": budget.get_amount(),
                                   "status": budget.get_status()} for category, budget in self.__budgets.items()}
        }
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Ошибка при сохранении данных: {e}")

    def _load_data(self):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.__expenses = [Expense(**expense_data) for expense_data in data.get("expenses", [])]
                self.__budgets = {
                    category: Budget(category=category,
                                     spent_amount=data["budgets"][category]["spent amount"],
                                     amount=data["budgets"][category]["amount"],
                                     status=data["budgets"][category]["status"])
                    for category in data.get("budgets", {})}

        except FileNotFoundError:
            self.__expenses = []
            self.__budgets = {}

        except (IOError, json.JSONDecodeError, ValueError) as e:
            print(f"Ошибка при загрузке данных: {e}. Начинаем с чистыми данными.")
            self.__expenses = []
            self.__budgets = {}
