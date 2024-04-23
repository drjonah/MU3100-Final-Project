import customtkinter, os
from PIL import Image
from tkinter.filedialog import askopenfilename, askdirectory
from compiler import compile_score
from player import play
from views.scoreInformation import ScoreInformation
from views.help import HelpInformation

# Initialize PATH for assets
cd = os.path.dirname(os.path.abspath(__file__))
cd_ = os.path.dirname(cd)
cd__ = os.path.dirname(cd_)
PATH = os.path.join(cd__, "assets")

BUTTON_WIDTH = 140
BUTTON_PADDING = 5
IMAGE_SIZE = (20, 20)

class UtilBar(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Init frame properties
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=1)
        # self.grid_columnconfigure(5, weight=1)

        # Initialize images
        self.img_play = customtkinter.CTkImage(Image.open(f"{PATH}/play.png").resize(IMAGE_SIZE))
        self.img_new = customtkinter.CTkImage(Image.open(f"{PATH}/new.png").resize(IMAGE_SIZE))
        self.img_open = customtkinter.CTkImage(Image.open(f"{PATH}/open.png").resize(IMAGE_SIZE))
        self.img_close = customtkinter.CTkImage(Image.open(f"{PATH}/close.png").resize(IMAGE_SIZE))
        self.img_help = customtkinter.CTkImage(Image.open(f"{PATH}/help.png").resize(IMAGE_SIZE))

        # Initialize buttons with images
        # play button
        self.play_button = customtkinter.CTkButton(
            master=self,
            text="Play",
            width=BUTTON_WIDTH,
            image=self.img_play,  # Assign the image here
            compound="left",  # Align the image to the left of the text
            command=self.listen_play
        )
        self.play_button.grid(row=0, column=0, padx=BUTTON_PADDING, pady=BUTTON_PADDING)

        # new file button
        self.new_button = customtkinter.CTkButton(
            self,
            text="New",
            width=BUTTON_WIDTH,
            image=self.img_new,
            compound="left",
            command=self.listen_new_file
        )
        self.new_button.grid(row=0, column=1, padx=BUTTON_PADDING, pady=BUTTON_PADDING)

        # open file button
        self.open_button = customtkinter.CTkButton(
            self,
            text="Open",
            width=BUTTON_WIDTH,
            image=self.img_open,
            compound="left",
            command=self.listen_open_file
        )
        self.open_button.grid(row=0, column=2, padx=BUTTON_PADDING, pady=BUTTON_PADDING)

        # close file button
        self.close_button = customtkinter.CTkButton(
            self,
            text="Close",
            width=BUTTON_WIDTH,
            image=self.img_close,
            compound="left",
            command=self.listen_close_tab
        )
        self.close_button.grid(row=0, column=3, padx=BUTTON_PADDING, pady=BUTTON_PADDING)

        # help button
        self.help_button = customtkinter.CTkButton(
            self,
            text="Help",
            width=BUTTON_WIDTH,
            image=self.img_help,
            compound="left",
            command=self.listen_help_tab
        )
        self.help_button.grid(row=0, column=4, padx=BUTTON_PADDING, pady=BUTTON_PADDING)

    def listen_play(self):
        tab_name = self.master.tab_view.get()
        file_path = self.master.tab_view.tabs[tab_name]

        if file_path is None:
            return 
        
        file_data, organum = compile_score(file_path)
        ScoreInformation().open_score(file_data, organum)
        # waits for the window to open before play
        self.after(100, lambda: play(organum))

    def listen_new_file(self):
        # open window to get file name
        dialog_window = customtkinter.CTkInputDialog(
            text="Enter file name:",
            title="Guido's Organum | New File"
        )
        file_name = dialog_window.get_input()

        # cancel new file action
        if file_name == None:
            return None
        
        file_name = file_name.strip()
        if file_name == "":
            return None

        # find file location
        file_path = askdirectory()
        full_file_path = file_path + "/" + file_name + ".organum" 

        # create file
        with open(f"{file_path}/{file_name}.organum", "w") as FILE:
            FILE.write("\\instruct {\n")
            FILE.write(f"    title: {file_name}\n")
            FILE.write("    composer:\n")
            FILE.write("}")

        # call add tab in filetab.py
        self.master.tab_view.add_tab(file_name, full_file_path)

    def listen_open_file(self) -> None:
        # open file
        file_path = askopenfilename(
            title="Select .organum file",
            filetypes=[("Organum files", "*.organum")]
        )

        # cancel open file action
        if file_path == "" or file_path == None:
            return

        file_name = os.path.basename(file_path) if file_path else None
        file_name = file_name.split(".organum")[0]

        # call add tab in filetab.py
        self.master.tab_view.add_tab(file_name, file_path)

    def listen_close_tab(self):
        # call close tab in filetab.py
        self.master.tab_view.close_tab(self.master.tab_view.get())

    def listen_help_tab(self):
        HelpInformation()
            
