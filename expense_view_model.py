from budget import Budget
from data_manager import DataManager
from expense import Expense


def format_currency(amount: float):
    return f"{amount:,.2f}".replace(',', ' ')


class ExpenseViewModel:
    def __init__(self, data_manager: DataManager):
        self.__data_manager = data_manager
        self.__expenses = []
        self.__budgets = {}

        self.on_data_changed = lambda: None

    def on_data_changed(self):
        return None

    def update_data(self):
        self.__expenses = self.__data_manager.get_expenses()
        self.__budgets = {budget.get_category(): budget for budget in self.__data_manager.get_all_budgets()}
        self.on_data_changed()

    def add_expense(self, category: str, amount: float, description: str):
        try:
            expense = Expense(category, amount, description)
            self.__data_manager.add_expense(expense)
            self.update_data()
            return True, "Расход успешно добавлен!"
        except ValueError as e:
            return False, str(e)

    def add_budget(self, category: str, amount: float):
        try:
            budget = Budget(category, amount)
            self.__data_manager.add_budget(budget)
            self.update_data()
            return True, f"Бюджет для '{category}' установлен в {format_currency(amount)}."
        except ValueError as e:
            return False, str(e)

    def delete_expense(self, expense_to_delete: Expense):

        if expense_to_delete in self.__expenses:
            self.__expenses.remove(expense_to_delete)
            self.update_data()
            return True, "Расход удален."

        return False, "Расход не найден."

    def get_expenses_by_category(self, category: str):
        return [expense for expense in self.__expenses if expense.get_category().lower() == category.lower()]

    def get_total_expenses(self):
        return sum(expense.__int__() for expense in self.__expenses)

    def get_budget_status(self, category: str):
        budget = self.__budgets.get(category)

        if not budget:
            return 0.0, 0.0,

        spent_amount = sum(expense.__int__() for expense in self.get_expenses_by_category(category))
        remaining = budget.__int__() - spent_amount

        if remaining >= 0:
            status = f"Осталось: {format_currency(remaining)}"
        else:
            status = f"Превышен на: {format_currency(-remaining)}"

        return spent_amount, budget.__int__(), status

    def get_all_categories(self):
        return sorted(list(set(budget for budget in self.__budgets)))

    def get_all_expenses(self):
        return self.__expenses

    def get_budgets(self):
        return list(self.__budgets.values())
