import tkinter as tk


from .pages import *
from .gui_utils import MenuBar, OpenNewWindow

class MainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        main_frame = tk.Frame(self, bg="black", height=200, width=100)
        main_frame.pack_propagate(0)
        main_frame.pack()
        # Set the icon and the title of the window
        self.iconbitmap('resources/gui/icon.ico')
        self.title("Language Trainer")

        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Resize the window to the screen size
        self.geometry("{0}x{1}+0+0".format(self.winfo_screenwidth(), self.winfo_screenheight()))
        # Prevent the window from resizing
        self.resizable(False, False)

        self.frames = {}

        for F in ALL_PAGES:
            frame = F(main_frame, self, home_page=HomePage)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Configure the menu bar
        self.show_frame(HomePage)
        menubar = MenuBar(self)
        tk.Tk.config(self, menu=menubar)
    
    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def OpenNewWindow(self):
        OpenNewWindow()

    def Quit_application(self):
        self.destroy()