from ..gui_utils import GUI

class SettingsPage(GUI):
    def __init__(self, parent, controller, home_page):
        GUI.__init__(self, parent)
        button_texts = ['Coming Soon', 'back']
        navigation_pages = [lambda:0, home_page]
        h, w = controller.winfo_screenheight(), controller.winfo_screenwidth()
        for i in range(len(button_texts)):
            self.packed_buttons += 1
            btn = self.create_button(controller, button_texts[i], navigation_pages[i], width=w//30, height=h//20)
            btn.pack()