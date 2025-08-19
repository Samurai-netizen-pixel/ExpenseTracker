def format_currency(amount: int | float):
    return f"{amount:,.2f}".replace(',', ' ')


class Budget:
    def __init__(self, category: str, amount: int | float, spent_amount: int | float = 0, status: str = None):
        if not isinstance(category, str) or not category:
            raise ValueError("Категория должна быть непустой строкой.")

        if not isinstance(spent_amount, (int, float)) or amount <= 0:
            raise ValueError("Сумма трат должна быть положительным числом.")

        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Сумма бюджета должна быть положительным числом.")

        self.__category = category
        self.__spent_amount = spent_amount
        self.__amount = amount
        self.__status = status

    def __str__(self):
        return f"{self.__category}: {format_currency(self.__spent_amount)} / {format_currency(self.__amount)} ({self.__status})"

    def __repr__(self):
        return f"Budget(category='{self.__category}', amount={self.__amount})"

    def get_category(self):
        return self.__category

    def __int__(self):
        return self.__amount
