from tkinter import *
from ..gui_utils import GUI

class TranslationTestMenu(GUI):
    def __init__(self, parent, controller, home_page):
        GUI.__init__(self, parent)
        title = Label(self.main_frame, font=("Verdana", 20), text="Translation Test")
        title.pack()

        button_texts = ['English to Target', 'Target to English', "Home"]
        commands = [Target2EnglishTest, English2TargetTest, home_page]

        h, w = controller.winfo_screenheight(), controller.winfo_screenwidth()
        for i in range(len(button_texts)):
            self.packed_buttons += 1
            btn = self.create_button(controller, button_texts[i], commands[i], height=h//40, width=w//20)
            btn.pack()

class Target2EnglishTest(GUI):
    def __init__(self, parent, controller, home_page, direction='Forward'):
        GUI.__init__(self, parent)
        title = Label(self.main_frame, font=("Verdana", 20), text="Translation Test")
        title.pack()

        self.direction = direction
        # Fit the page to the screen
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        h, w = controller.winfo_screenheight(), controller.winfo_screenwidth()
        entry = Entry(self, width=30)
        entry.place(relx=0.2, rely=0.1)
        
        btn = self.create_button(controller, 'Translate', self.translate, height=h//40, width=w//20)
        btn.place(relx=0.1, rely=0.1)

        btn = self.create_button(controller, 'Home', home_page, width=w//100, height=h//1000)
        btn.place(relx=0.8, rely=0.8)
    
class English2TargetTest(Target2EnglishTest):
    def __init__(self, parent, controller, home_page, direction='Backward'):
        super().__init__(parent, controller, home_page, direction)