from tkinter import *
from turtle import bgcolor

from ..gui_utils import GUI
from ..pages import TranslationTestMenu

class HomePage(GUI):
    def __init__(self, parent, controller, *args, **kwargs):
        GUI.__init__(self, parent)
        
        button_texts = ['Translate', 'Exit']
        navigation_pages = [TranslationTestMenu, 'Exit']
        for i in range(len(button_texts)):
            self.packed_buttons += 1
            btn = self.create_button(controller, button_texts[i], navigation_pages[i])
            btn.pack()