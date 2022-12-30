import json, os

import warnings
from json import JSONDecodeError

from pygame_menu.examples import create_example_window

from typing import Optional
from ..utils.default_settings import DEFAULT_SETTINGS
from .pygame_menu import PygameMenu

class SettingsHandler(dict):
    def __init__(self, resource_dir, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = f'{resource_dir}/settings.json'
        self.settings_menu = None
        self._get_settings()
        self.settings_restored = False
    
    def restore_default_settings(self):
        """ Restore all the settings to the default value"""
        self.save_settings(DEFAULT_SETTINGS)
        self._copy_settings_from_dict(DEFAULT_SETTINGS)
        if self.settings_menu is not None:
            # FIXME: Figure out how to exit or change the value after the settings are returned to default
            self.settings_restored = True


    def save_settings(self, settings:Optional[dict]=None):
        """
        Saves the settings to the appropriate files (can be used when the settings are changed by the user)
        :param settings: a dictionary containing the settings of the application, if no settings are in the input,
         then the settings of the app are saved
        """
        if settings is None:
            settings = self.copy()
        with open(self.path, 'w') as f:
            json.dump(settings, f)
    
    def _get_settings(self):
        """ Returns the settings of the application. If no settings file are found it creates and loads the default settings"""
        try:
            with open(self.path, 'r') as f:
                settings = json.load(f)
            self._copy_settings_from_dict(settings)
        except:
            warnings.warn('Failed to recover settings file. Restoring to default settings.')
            self.restore_default_settings()

    def display_options(self, screen=None):
        # FIXME: this still doesn't work, all the program will migrate to pygame_menu for menus
        if not screen:
            screen = create_example_window('Settings', self['Screen Resolution'])
        settings_menu = PygameMenu('Settings Menu', self['Screen Resolution'],
                                    (0.8, 0.7), 'Options')
        
        w, h = self['Screen Resolution']
        for name, default in [('Screen Width', w), ('Screen Height', h)]:
            settings_menu.add_number_input(name + '  ', default=default, id=name, maxchar=5)
        
        settings_menu.add.toggle_switch('Full Screen', self['Full Screen'],
                                toggleswitch_id='Full Screen')

        text_sections = [(key, self[key]) for key in
                ['Included Categories', 'Excluded Categories', 'Database', 'Excel Sheet']]

        for name, default_value in text_sections:
            settings_menu.add_text_input(name, default=default_value, input_id=name)
        settings_menu.add_number_input('Number of Samples  ', id="Sample Size", default=self["Sample Size"])

        settings_menu.add.button('Open Database', self.open_db, button_id='open_db')  # Call function
        settings_menu.add.button('Restore original values', self.restore_default_settings)

        self.settings_menu = settings_menu
        self.settings_menu.mainloop(screen, bgcolor=(0, 0, 0))
        self.update_settings_from_menu(self.settings_menu.get_input_data())

    def open_db(self):
        os.system("start EXCEL.EXE " + '"' + self['Database'] + '"')
    
    def _copy_settings_from_dict(self, stg_dict):
        for key, value in stg_dict.items():
            self[key] = value

    def update_settings_from_menu(self, menu_data):
        if self.settings_restored:
            self.settings_restored = False
            return
        menu_data['Screen Resolution'] = [menu_data.pop("Screen Width"), menu_data.pop("Screen Height")]
        for key in menu_data.keys():
            self[key] = menu_data[key]

    def sample_length_varied(self):
        return len(self['Sampled Words']) != self['Sample Size']

    def sheet_changed(self):
        return self['Excel Sheet'] != self['Source of Sampled Words']

    def set_sampled_words(self, sampled_words):
        self['Sampled Words'] = list(sampled_words)
        self['Source of Sampled Words'] = self['Excel Sheet']
