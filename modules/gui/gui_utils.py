import tkinter as tk
from tkinter import Button
from tkinter import ttk
def popupmsg(msg):
    popup = tk.Tk()
    popup.wm_title("!")
    label = ttk.Label(popup, text=msg, font=('Verdana', 10))
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    popup.mainloop()

class GUI(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.main_frame = tk.Frame(self)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.packed_buttons = 0
    
    def create_button(self, controller, text, navigation_page, command = None, **kwargs):
        button = Button(self, text=text, width=30, bg='#84CEEB')
        if command:
            button.configure(command=command, **kwargs)
        elif navigation_page != 'Exit':
            button.configure(command=lambda: controller.show_frame(navigation_page), **kwargs)
        else:
            button.configure(command=lambda: controller.Quit_application(), **kwargs)
        return button
    
class MenuBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)

        menu_file = tk.Menu(self, tearoff=0)
        self.add_cascade(label="File", menu=menu_file)
        folders_menu = tk.Menu(menu_file, tearoff=0)
        menu_file.add_cascade(label="Open Folder", menu=folders_menu)
        folders_menu.add_command(label="Vocabulary Database", command=lambda: popupmsg('Coming soon!'))
        menu_file.add_separator()
        menu_file.add_command(label="Exit", command=lambda: parent.Quit_application())

        menu_help = tk.Menu(self, tearoff=0)
        menu_help.add_command(label="Translation Test", command=lambda:popupmsg('Coming soon!'))
        menu_help.add_command(label='Singular and Plural Test', command=lambda: popupmsg('Coming soon!'))
        menu_help.add_command(label="Noun Genders Test", command=lambda: parent.OpenNewWindow())
        self.add_cascade(label="Help", menu=menu_help)

class OpenNewWindow(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        main_frame = tk.Frame(self)
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand="true")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        self.title("Here is the Title of the Window")
        self.geometry("500x500")
        self.resizable(0, 0)

        frame1 = ttk.LabelFrame(main_frame, text="This is a ttk LabelFrame")
        frame1.pack(expand=True, fill="both")

        label1 = tk.Label(frame1, font=("Verdana", 20), text="OpenNewWindow Page")
        label1.pack(side="top")
