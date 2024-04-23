import customtkinter, os, webbrowser
from PIL import Image

# Initialize PATH for assets
cd = os.path.dirname(os.path.abspath(__file__))
cd_ = os.path.dirname(cd)
cd__ = os.path.dirname(cd_)
PATH = os.path.join(cd__, "assets")

BUTTON_WIDTH = 140
BUTTON_PADDING = 5
IMAGE_SIZE = (20, 20)
DIRECTION_IMAGE_SIZE = (550, 650)

GITHUB = "https://github.com/drjonah/MU3100-Final-Project"
WIKI = "https://en.wikipedia.org/wiki/Guidonian_hand"
PAPER = "https://google.com/"

class HelpInformation(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("600x700")
        self.title("Guido's Organum | MU 3100")
        self.resizable(False, False)

        # Configure column weights to center the buttons horizontally
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)

        # images
        self.img_github = customtkinter.CTkImage(Image.open(f"{PATH}/github.png"))
        self.img_download = customtkinter.CTkImage(Image.open(f"{PATH}/download.png"))
        self.img_wiki = customtkinter.CTkImage(Image.open(f"{PATH}/wiki.png"))
        self.img_paper = customtkinter.CTkImage(Image.open(f"{PATH}/paper.png"))
        self.img_help = customtkinter.CTkImage(Image.open(f"{PATH}/directions.png"), size=DIRECTION_IMAGE_SIZE)

        # example
        self.example_file_name = "example.organum"
        self.example_file_path = PATH + "/" + self.example_file_name

        # load image
        direction_image = customtkinter.CTkLabel(
            master=self,
            image=self.img_help,
            text=""
        )
        direction_image.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=BUTTON_PADDING, pady=BUTTON_PADDING)

        # load buttons
        self.wiki_button = customtkinter.CTkButton(
            master=self,
            text="Wiki",
            width=BUTTON_WIDTH,
            image=self.img_wiki,
            compound="left",
            command=lambda: webbrowser.open(WIKI)
        )
        self.wiki_button.grid(row=1, column=0, padx=BUTTON_PADDING, pady=BUTTON_PADDING)

        self.github_button = customtkinter.CTkButton(
            master=self,
            text="GitHub",
            width=BUTTON_WIDTH,
            image=self.img_github,
            compound="left",
            command=lambda: webbrowser.open(GITHUB)
        )
        self.github_button.grid(row=1, column=1, padx=BUTTON_PADDING, pady=BUTTON_PADDING)

        self.paper_button = customtkinter.CTkButton(
            master=self,
            text="Research",
            width=BUTTON_WIDTH,
            image=self.img_paper,
            compound="left",
            command=lambda: webbrowser.open(PAPER)
        )
        self.paper_button.grid(row=1, column=2, padx=BUTTON_PADDING, pady=BUTTON_PADDING)

        self.download_button = customtkinter.CTkButton(
            master=self,
            text="Example",
            width=BUTTON_WIDTH,
            image=self.img_download,
            compound="left",
            command=self.open_example
        )
        self.download_button.grid(row=1, column=3, padx=BUTTON_PADDING, pady=BUTTON_PADDING)

    def open_example(self):
        self.master.tab_view.add_tab(self.example_file_name, self.example_file_path)
