import re
import pygame_menu

from ..utils.pygame_themes import get_theme
from ..utils import rel2abs
class PygameMenu(pygame_menu.Menu):
    def __init__(self, theme_name, screen_size, menu_rel_size, title):
        self.theme = get_theme(theme_name)
        w, h = rel2abs(menu_rel_size, screen_size)
        super().__init__(
            height = h,
            onclose=pygame_menu.events.EXIT,  # User press ESC button
            theme=self.theme,
            title=title,
            width = w
        )

    def mainloop(self, screen, bgcolor=None):
        if bgcolor is not None:
            screen.fill(bgcolor)
        super().mainloop(screen)
    
    def add_number_input(self, prompt, id=None, default=0, maxchar=4, **kwargs):
        if id is None:
            # If no id is provided, the id will be all non alphanumeric
            # characters with _ instead of spaces
            id = re.sub(r'[^ \w+]', '', prompt)
            id = id.lower().strip().replace(' ', '_')
        self.add.text_input(
                prompt,
                default=default,
                maxchar=maxchar,
                maxwidth=maxchar,
                textinput_id=id,
                input_type=pygame_menu.locals.INPUT_INT,
                **kwargs
                )


    def add_text_input(self, prompt, id=None, default=0, maxwidth=19, **kwargs):
        if id is None:
            # If no id is provided, the id will be all non alphanumeric
            # characters with _ instead of spaces
            id = re.sub(r'[^ \w+]', '', prompt)
            id = id.lower().strip().replace(' ', '_')
        self.add.text_input(
            prompt,
            maxwidth=maxwidth,
            textinput_id=id,
            input_underline='_'
        )