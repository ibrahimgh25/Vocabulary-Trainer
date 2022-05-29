from tkinter import *
from turtle import bgcolor

from ..gui_utils import GUI
from .translation_test import TranslationTestMenu
from .settings_page import SettingsPage

class HomePage(GUI):
    def __init__(self, parent, controller, *args, **kwargs):
        GUI.__init__(self, parent)
        
        button_texts = ['Translate', 'Settings', 'Exit']
        navigation_pages = [TranslationTestMenu, SettingsPage, 'Exit']
        h, w = controller.winfo_screenheight(), controller.winfo_screenwidth()
        for i in range(len(button_texts)):
            self.packed_buttons += 1
            btn = self.create_button(controller, button_texts[i], navigation_pages[i], width=w//30, height=h//50)
            btn.pack()