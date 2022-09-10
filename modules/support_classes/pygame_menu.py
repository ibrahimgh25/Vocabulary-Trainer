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
        self._disable_exit = True

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


    def add_text_input(self, prompt, input_id=None, default='', maxwidth=19, **kwargs):
        if not input_id:
            # If no id is provided, the id will be all non-alphanumeric
            # characters with _ instead of spaces
            input_id = re.sub(r'[^ \w+]', '', prompt)
            input_id = input_id.lower().strip().replace(' ', '_')
        self.add.text_input(
            prompt,
            maxwidth=maxwidth,
            textinput_id=str(input_id),
            input_underline='_',
            default=default,
            **kwargs
        )

    def get_input_id(element_name:str) -> str:
        """
        Transforms a string into an id, e.g.:
         'Start Menu **' gives 'start_menu'
         '(re34 and 5' gives 're34_and_5'
        """
        # If no id is provided, the id will be generated from the name of the element,
        # e.g. if the name of the element is 'Start Menu **' this function will return
        input_id = re.sub(r'[^ \w+]', '', element_name)
        return input_id.lower().strip().replace(' ', '_')