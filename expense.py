class Expense:
    def __init__(self, category: str, amount: int | float, description: str = ""):
        if not isinstance(category, str) or not category:
            raise ValueError("Категория должна быть непустой строкой.")

        if not isinstance(amount, (int, float)) or amount == 0:
            raise ValueError("Сумма должна быть положительным числом.")

        self.__category = category
        self.__amount = amount
        self.__description = description

    def __str__(self):
        return f"{self.__category}: {self.__amount:.2f} - {self.__description}"

    def __repr__(self):
        return f"Expense(category='{self.__category}', amount={self.__amount}, description='{self.__description}')"

    def get_category(self):
        return self.__category

    def __int__(self):
        return self.__amount

    def get_description(self):
        return self.__description
