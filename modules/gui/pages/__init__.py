from .translation_test import (
    TranslationTestMenu,
    English2TargetTest,
    Target2EnglishTest)

from .home import HomePage
from .settings_page import SettingsPage

# Create a list with all the imported pages
ALL_PAGES = [
    HomePage,
    TranslationTestMenu,
    English2TargetTest,
    Target2EnglishTest,
    SettingsPage
]