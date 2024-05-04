import customtkinter, os
from PIL import Image
from src.player import play, stop

# Initialize PATH for assets
cd = os.path.dirname(os.path.abspath(__file__))
cd_ = os.path.dirname(cd)
cd__ = os.path.dirname(cd_)
PATH = os.path.join(cd__, "assets")

BUTTON_WIDTH = 130
BUTTON_PADDING = 5
IMAGE_SIZE = (20, 20)

class ScoreInformation(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("300x120")
        self.title("Guido's Organum | MU 3100")
        self.resizable(False, False)

        self.img_replay = customtkinter.CTkImage(Image.open(f"{PATH}/replay.png").resize(IMAGE_SIZE))
        self.img_stop = customtkinter.CTkImage(Image.open(f"{PATH}/stop.png").resize(IMAGE_SIZE))

        # escape key
        self.bind('<Escape>', lambda event: self.destroy())

    def open_score(self, file_data: dict, organum: list):
        self.grid_columnconfigure(0, weight=1)

        score_title = file_data["title"] if file_data["title"] != "" else "Unknown Title"
        score_composer = file_data["composer"] if file_data["composer"] != "" else "Unknown Composer"

        self.title = customtkinter.CTkLabel(
            master=self,
            text=score_title
        )
        self.title.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=BUTTON_PADDING, pady=BUTTON_PADDING)
        self.title.cget("font").configure(size=18)

        self.composer = customtkinter.CTkLabel(
            master=self,
            text=score_composer
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

        self.stop_button = customtkinter.CTkButton(
            master=self,
            text="Stop",
            width=BUTTON_WIDTH,
            image=self.img_stop,
            compound="left",
            command=lambda: stop()
        )
        self.stop_button.grid(row=2, column=1, padx=BUTTON_PADDING, pady=BUTTON_PADDING)

        # bind key
        self.bind("<Command-p>", lambda event: play(organum))
        self.bind("<Command-s>", lambda event: stop())