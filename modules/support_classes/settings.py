import json

import warnings

class SettingsHandler(dict):
    def __init__(self, resource_dir, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = f'{resource_dir}/settings.json'
        self._get_settings()
    
    def restore_default_settings(self):
        """ Restore all the settings to the default value"""
        settings = {
            'Screen Resolution':(750, 500),
            'Head Color':(255, 324, 102),
            'Text Color':(240, 240, 240),
            'Database':'resources/german_database.xlsx',
            'Excel Sheet':'A1'
        }
        self.save_settings(settings)
        self._copy_settings_from_dict(settings)
    
    def save_settings(self):
        """
        Saves the settings to the appropriate files (can be used when the settings are changed by the user)
        :param settings: a dictionary containing the settings of the application

        """
        with open(self.path, 'w') as f:
            json.dump(self.copy(), f)
    
    def _get_settings(self):
        """ Returns the settings of the application. If no settings file are found it creates and loads the default settings"""
        try:
            with open(self.path, 'r') as f:
                settings = json.load(f)
        except:
            warnings.warn('Failed to recover setttings file. Restoring to default settings.')
            settings = self.restore_default_settings()
        self._copy_settings_from_dict(settings)
    
    def settings_menu(self, screen):
        pass

    def _copy_settings_from_dict(self, stg_dict):
        for key, value in stg_dict.items():
            self[key] = value