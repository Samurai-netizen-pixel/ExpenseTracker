from budget import Budget
from expense import Expense


class DataManager:
    def __init__(self):
        self.__expenses = []
        self.__budgets = {}

    def add_expense(self, expense: Expense):
        self.__expenses.append(expense)

    def get_expenses(self):
        return self.__expenses

    def add_budget(self, budget: Budget):
        self.__budgets[budget.get_category()] = budget

    def get_budget(self, category: str):
        return self.__budgets.get(category)

    def get_all_budgets(self):
        return list(self.__budgets.values())
