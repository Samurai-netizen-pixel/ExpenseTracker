class Budget:
    def __init__(self, category: str, amount: float):

        if not isinstance(category, str) or not category:
            raise ValueError("Категория должна быть непустой строкой.")

        if not isinstance(amount, (int, float)) or amount == 0:
            raise ValueError("Сумма бюджета должна быть положительным числом.")

        self.__category = category
        self.__amount = amount

    def __str__(self):
        return f"Бюджет на {self.__category}: {self.__amount:.2f}"

    def __repr__(self):
        return f"Budget(category='{self.__category}', amount={self.__amount})"

    def get_category(self):
        return self.__category

    def __int__(self):
        return self.__amount
