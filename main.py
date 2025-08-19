from application_model import ApplicationModel
from application_view import ApplicationView
from application_view_model import ApplicationViewModel

if __name__ == "__main__":
    data_manager = ApplicationModel()
    viewmodel = ApplicationViewModel(data_manager)
    app = ApplicationView(viewmodel)
    app.mainloop()
