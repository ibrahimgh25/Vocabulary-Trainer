from tkinter import *
from ..gui_utils import GUI

class TranslationTesMenu(GUI):
    def __init__(self, parent, controller, home_page):
        GUI.__init__(self, parent)
        title = Label(self.main_frame, font=("Verdana", 20), text="Translation Test")
        title.pack()

        button_texts = ['Translation Test', 'Target to English', "Home"]
        commands = [lambda: print(1), lambda: print(1), home_page]
        for i in range(len(button_texts)):
            self.packed_buttons += 1
            btn = self.create_button(controller, button_texts[i], commands[i])
            btn.pack()

class TranslationTestPage(GUI):
    def __init__(self, parent, controller, home_page, direction='Forward'):
        GUI.__init__(self, parent)
        title = Label(self.main_frame, font=("Verdana", 20), text="Translation Test")
        title.pack()

        self.direction = direction

        entry = Entry(self, width=30)
        entry.pack()

        btn = self.add_button(controller, 'Home', home_page)
        btn.pack()