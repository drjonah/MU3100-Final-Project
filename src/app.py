import customtkinter
from src.views import FileTabs, UtilBar

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x800")
        self.title("Guido's Organum | MU 3100")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.resizable(False, False)

        # util bar
        self.my_frame = UtilBar(master=self)
        self.my_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # file tab bar
        self.tab_view = FileTabs(master=self)
        self.tab_view.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # escape key
        self.bind("<Escape>", lambda event: self.destroy())