import customtkinter, platform

class FileTabs(customtkinter.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # create storage
        self.tabs = {}
        self.tabs_line_numbers = {}

        # add the initial empty page
        if not self.tabs.keys():
            self.add_tab("None", None, True)

    def add_tab(self, file_name: str, file_path: str, empty=False):
        # check if file_name is already in use
        if file_name in self.tabs.keys() or file_path in self.tabs.values():
            return

        # add and confiure tab
        tab = self.add(file_name)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        # empty tab 
        if empty:
            # add empty label
            tab.label = customtkinter.CTkLabel(
                master=tab,
                text="No file selected!",
                fg_color="transparent"
            )
            tab.label.grid(row=0, column=0, sticky="nsew")

            self.tabs["None"] = None
        else:
            # add tab to dict and load file
            self.tabs[file_name] = file_path
            self.load_file(tab, file_name, file_path)

            # check if empty tag still exists
            if "None" in self.tabs.keys():
                self.close_tab("None")
    
    def close_tab(self, tab_name: str):
        self.delete(tab_name)
        del self.tabs[tab_name]

        if not self.tabs.keys():
            # self.empty_tab()
            self.add_tab("None", None, True)

    def load_file(self, tab: customtkinter.CTkFrame, tab_name: str, file_path: str):
        # initialize
        tab.grid_columnconfigure(0, weight=0)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_columnconfigure(2, weight=0)

        # make scrollbar
        tab.scroll_bar = customtkinter.CTkScrollbar(
            master=tab
        )
        tab.scroll_bar.grid(row=0, column=2, sticky="nsew")

        # make textbox
        tab.textbox = customtkinter.CTkTextbox(
            master=tab,
            corner_radius=0,
            activate_scrollbars=False,
            undo=True
        )
        tab.textbox.grid(row=0, column=1, sticky="nsew")

        # dump file
        with open(file_path, "r") as FILE:
            file = FILE.read()
            line_count = file.count("\n")
        tab.textbox.insert("0.0", file)

        # bind to textbox
        tab.textbox.bind("<KeyRelease>", lambda event: self.autosave(tab_name, file_path))
        tab.textbox.bind("<Tab>", lambda event: self.custom_tab(tab_name))

        # make scroll frame for line numbers
        tab.line_numbers = customtkinter.CTkTextbox(
            master=tab,
            width=30,
            corner_radius=0,
            activate_scrollbars=False
        )
        tab.line_numbers.grid(row=0, column=0, sticky="nsew")
        self.update_line_numbers(tab_name, line_count)

        # create scroll bar for the text boxes
        def control_scrollbar(*args):
            tab.line_numbers.yview(*args)
            tab.textbox.yview(*args)

        # connfigure the textboxes
        tab.scroll_bar.configure(command=control_scrollbar)
        tab.textbox.configure(yscrollcommand=tab.scroll_bar.set)
        tab.line_numbers.configure(yscrollcommand=tab.scroll_bar.set)

        # bind mousewheel events to both text boxes
        tab.textbox.bind("<MouseWheel>", lambda event: self.on_mousewheel(event, tab))
        tab.line_numbers.bind("<MouseWheel>", lambda event: self.on_mousewheel(event, tab))

    def autosave(self, tab_name: str, file_path: str):
        text = self.tab(tab_name).textbox.get("0.0", "end")

        # save the text to the file
        with open(file_path, "w") as FILE:
            FILE.write(text)
            
        line_count = text.count("\n")

        if line_count != self.tabs_line_numbers[tab_name]:
            self.update_line_numbers(tab_name, line_count)

    def update_line_numbers(self, tab_name: str, line_numbers: int):
        # get tab and number of lines
        tab_reference = self.tab(tab_name)
        line_nums = [str(x) for x in range(1, line_numbers+1)]

        # update line numbers
        tab_reference.line_numbers.configure(state="normal")
        tab_reference.line_numbers.delete("0.0", "end")
        tab_reference.line_numbers.insert("0.0", ("\n".join(line_nums)))
        tab_reference.line_numbers.configure(state="disabled")

        # update reference
        self.tabs_line_numbers[tab_name] = line_numbers
    
    def custom_tab(self, tab_name: str):
        # insert tab
        self.tab(tab_name).textbox.insert("insert", " " * 4)
        # ignore regular tab
        return "break" 
    
    def on_mousewheel(self, event, tab):
        if platform.system() == 'Windows':
            tab.textbox.yview_scroll(-1 * int(event.delta/120), "units")
            tab.line_numbers.yview_scroll(-1 * int(event.delta/120), "units")
        elif platform.system() == 'Darwin':
            tab.textbox.yview_scroll(-1 * int(event.delta), "units")
            tab.line_numbers.yview_scroll(-1 * int(event.delta), "units")