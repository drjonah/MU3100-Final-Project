import customtkinter, os
from PIL import Image
from player import play

# Initialize PATH for assets
cd = os.path.dirname(os.path.abspath(__file__))
cd_ = os.path.dirname(cd)
cd__ = os.path.dirname(cd_)
PATH = os.path.join(cd__, "assets")

BUTTON_WIDTH = 140
BUTTON_PADDING = 5
IMAGE_SIZE = (20, 20)

class ScoreInformation(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("300x150")
        self.title("Guido's Organum | MU 3100")
        self.resizable(False, False)

        self.img_replay = customtkinter.CTkImage(Image.open(f"{PATH}/replay.png").resize(IMAGE_SIZE))
        self.img_close = customtkinter.CTkImage(Image.open(f"{PATH}/close.png").resize(IMAGE_SIZE))

    def open_score(self, file_data: dict, organum: list):
        self.grid_columnconfigure(0, weight=1)

        self.title = customtkinter.CTkLabel(
            master=self,
            text=file_data["title"]
        )
        self.title.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=BUTTON_PADDING, pady=BUTTON_PADDING)
        self.title.cget("font").configure(size=18)

        self.composer = customtkinter.CTkLabel(
            master=self,
            text=file_data["composer"]
        )
        self.composer.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=BUTTON_PADDING, pady=BUTTON_PADDING)
        self.composer.cget("font").configure(size=12)

        self.replay_button = customtkinter.CTkButton(
            master=self,
            text="Replay",
            width=BUTTON_WIDTH,
            image=self.img_replay,
            compound="left",
            command=lambda: play(organum)
        )
        self.replay_button.grid(row=2, column=0, padx=BUTTON_PADDING, pady=BUTTON_PADDING)

        self.close_button = customtkinter.CTkButton(
            master=self,
            text="Close",
            width=BUTTON_WIDTH,
            image=self.img_close,
            compound="left",
            command=lambda: self.destroy()
        )
        self.close_button.grid(row=2, column=1, padx=BUTTON_PADDING, pady=BUTTON_PADDING)
