import json, os

import warnings
from .default_settings import DEFAULT_SETTINGS

class SettingsHandler(dict):
    def __init__(self, resource_dir, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = f'{resource_dir}/settings.json'
        self._get_settings()
    
    def restore_default_settings(self):
        """ Restore all the settings to the default value"""
        self.save_settings(DEFAULT_SETTINGS)
        self._copy_settings_from_dict(DEFAULT_SETTINGS)
    
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
            warnings.warn('Failed to recover setttings file. Restoring to default settings.')
            self.restore_default_settings()
    
    def settings_menu(self, screen):
        pass

    def _copy_settings_from_dict(self, stg_dict):
        for key, value in stg_dict.items():
            self[key] = value