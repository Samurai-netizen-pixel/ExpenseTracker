from data_manager import DataManager
from main_window import MainWindow
from expense_view_model import ExpenseViewModel

if __name__ == "__main__":
    data_manager = DataManager()
    viewmodel = ExpenseViewModel(data_manager)
    app = MainWindow(viewmodel)
    app.mainloop()
