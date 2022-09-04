import pygame_menu

def get_theme(theme_name:str):
    fnc_name = theme_name.lower().replace(' ', '_') + '_theme'
    return globals()[fnc_name]()

def main_menu_theme():
    theme = pygame_menu.themes.THEME_ORANGE.copy()
    theme.title_font = pygame_menu.font.FONT_COMIC_NEUE
    theme.widget_font = pygame_menu.font.FONT_COMIC_NEUE
    theme.widget_font_size = 30
    return theme