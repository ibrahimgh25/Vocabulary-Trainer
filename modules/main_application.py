from optparse import Option
from typing import Iterable, Tuple, Optional
import pygame
import json, os
import time
import sys

from .question_handler import QuestionHandler

class TrainerApp:
    """ This class contains the main application that will handle the front-end, it will also control the back-end
         class (QuestionHandler)"""
   
    def __init__(self, resource_dir:str):
        self.resource_dir = resource_dir
        self.stg = self._get_settings()

        self.resource_dir = resource_dir
        self.question_handler = QuestionHandler(self.stg['Database'], self.stg['Excel Sheet'])

        self.status = 'reset'
        self.user_answer = ''
        
        img_size = self.stg['Screen Resolution']
        pygame.init()
        self.home_img = pygame.image.load(f'{resource_dir}/main_menu.jpg')
        self.home_img = pygame.transform.scale(self.home_img, img_size)


        self.bg = pygame.image.load(f'{resource_dir}/background.jpg')
        self.bg = pygame.transform.scale(self.bg, img_size)

        self.screen = pygame.display.set_mode(img_size)
        pygame.display.set_caption('Vocabulary Trainer')

    def _get_settings(self):
        """ Returns the settings of the application. If no settings file are found it creates and loads the default settings"""
        settings_path = f'{self.resource_dir}/settings.json'
        if not os.path.exists(settings_path):
            self.restore_default_settings()
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        return settings
    
    def _save_settings(self, settings):
        """
        Saves the settings to the appropriate files (can be used when the settings are changed by the user)
        :param settings: a dictionary containing the settings of the application

        """
        with open(f'{self.resource_dir}/settings.json', 'w') as f:
            json.dump(settings, f)

    def restore_default_settings(self):
        """ Restore all the settings to the default value"""
        settings = {
            'Screen Resolution':(750, 500),
            'Head Color':(255, 324, 102),
            'Text Color':(240, 240, 240),
            'Database':'resources/german_database.xlsx',
            'Excel Sheet':'A1'
        }
        self._save_settings(settings)
        

    def draw_text(self, msg, rect,  fgcolor=(255, 255, 255), fsize=26, bgcolor=(0, 0, 0)):
        """
        Draws a rectangle and displays text in it on the active screen
        :param msg: the text to be displayed
        :param rect: the position of the drawn rectangle with the format (x, y, w, h)
        :param fgcolor:  the text RGB color (Default value = (255, 255, 255))
        :param fsize:  the text size (Default value = 26)
        :param bgcolor:  the rectangle RGB color (Default value = (0, 0, 0)
        Note: the function aligns the text with the center of the drawn rectangle
        """
        self.screen.fill(bgcolor, rect)
        pygame.draw.rect(self.screen, bgcolor, rect, 2)
        
        font = pygame.font.Font(None, fsize)
        text = font.render(msg, 1,fgcolor)
        center = (rect[0] + rect[2]//2, rect[1] + rect[3]//2)
        text_rect = text.get_rect(center=center)
        self.screen.blit(text, text_rect)
        pygame.display.update()   
    
    def add_options(self, options:Iterable[str], dimensions:dict)->tuple:
        """
        Add a list of options to a screen
        :param options: a list of strings containing the name of the options
        :params dimensions: dictionary contining the rel (in %) dimensions of the options
         it should contain the following keys: 
         - rel_y: the starting y relative to the height
         - rel_x: the starting x relative to the width
         - rel_w and rel_h: relative heights and widths of each options
         - rel_gap: the gap between two options
        :returns: a list of tuple with each element as follows (option_name, option_rect)
        """
        w, h = self.stg['Screen Resolution']
        # Divide by 100 each dimension
        dimensions = {x:y/100 for x, y in dimensions.items()}
        current_y = int(dimensions['rel_y']*h)
        start_x = int(dimensions['rel_x']*w)
        width, height = int(dimensions['rel_w']*w), int(dimensions['rel_h']*h)
        gap = int(dimensions['rel_gap']*h) # Distance between two options
        fsize = height//2
        output = []
        fcolor = (19, 161, 14)
        bgcolor = (255, 255, 255, 0)
        for option in options:
            output.append((option, (start_x, current_y, width, height)))
            self.draw_text(option, rect=output[-1][1], fsize=fsize, fgcolor=fcolor, bgcolor=bgcolor)
            current_y += gap + height
        return output
    
     
    def start(self):
        """ This function displays the main menu until the user chooses a valid option
            :returns: the name of the pressed option
        """
        self.reset_screen(self.home_img)
        self.status = 'idle'
        pygame.display.update()
        
        options = ['Practice',
                    'Show Scores',
                    'Settings',
                    'Exit'
                    ]
        dimensions = {'rel_y':29, 'rel_x':5, 'rel_w':35, 'rel_h':10, 'rel_gap':1.6}

        options = self.add_options(options, dimensions)
        return self.get_user_option(options)

    def choose_exercise(self):
        ''' Choose an exercise to either display its score or practice it'''
        self.reset_screen(self.home_img)
        options = ['Translate English to Target',
                    'Translate Target to English',
                    'Back'
                    ]
        dimensions = {'rel_y':29, 'rel_x':5, 'rel_w':35, 'rel_h':10, 'rel_gap':1.6}
        options = self.add_options(options, dimensions)
        return self.get_user_option(options)
        
    
    def get_user_option(self, options):
        ''' Returns what option the user chooses on a given screen'''
        while(True):
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.MOUSEBUTTONUP:
                matching_area = self.get_matching_area(options)
                if matching_area is not None:
                    return matching_area

    def get_matching_area(self, options:Iterable[Tuple]):
        """
        calculates which option a mouse click matches
        :param options: a list of tuples representing all the options in the page, has the form [(option_name, option_rect), ...]
        :returns: name of the matched option, if no option was matched it returns ''
        """
        x, y = pygame.mouse.get_pos()
        for option in options:
            rect = option[1]
            matching_x = x > rect[0] and x < rect[0] + rect[2]
            matching_y = y > rect[1] and y < rect[1] + rect[3]
            if matching_x and matching_y:
                return option[0]
        return ''
        
    def get_answer(self, question:str):
        """
        Displays a question on the screen and saves the answer provided by the user in self.user_answer
        :param question: the string containing the question
        """
        self.status = 'active'
        self.user_answer = ''
        self.reset_screen(self.bg)
        # draw the question
        self.draw_text(question, rect=(50,180,650,50), bgcolor=(237,125,49))
        while self.status == 'active':
    
            # update the text of user input
            self.draw_text(self.user_answer, rect=(50,250,650,50), bgcolor=(237,125,49))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.status = 'dead'
                    return
                elif event.type == pygame.KEYDOWN:
                    if self.status == 'active':
                        if event.key == pygame.K_BACKSPACE:
                            self.user_answer = self.user_answer[:-1]
                        elif event.key == pygame.K_RETURN:
                            return self.user_answer
                        else:
                            try:
                                self.user_answer += event.unicode
                            except:
                                pass
                       

    def display_question_results(self, correct_answer:str, answered_correctly:bool)->Optional[int]:
        """
        Displays the results for a question on the screen
        :param correct_answer: the correct answer to the question, diplayed below the answer given by the user
        :param answered_correctly: whether the user answered the question correctly
        :returns: 0 if the escape key was pressed, 1 if "enter" or "space' where pressed
        """
        if answered_correctly:
            bgcolor = (0, 0, 255)
        else:
            bgcolor = (255, 0, 0)

        # update the text of user input
        self.draw_text(correct_answer, rect=(50, 340, 650, 50), bgcolor=bgcolor)

        while(True):
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                self.status = 'dead'
                self.quit()
            elif event.type == pygame.KEYDOWN and event.key in [pygame.K_SPACE, pygame.K_RETURN] :
                return 1
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return 0
    
    def reset_screen(self, image):
        """
        Resets a given screen by displaying a new background image
        :param image: the image to display

        """
        self.screen.blit(image, (0,0))
        pygame.display.update()
    
    def quit(self):
        """ Performs the necessary actions before the application exits"""
        self.question_handler.save_database(self.stg['Database'], self.stg['Excel Sheet'])
        self.question_handler.save_all_scores()
        pygame.quit()
        sys.exit()
    
    def main_loop(self):
        """ The main loop of the application"""
        while(True):
            option = self.start()
            if option == 'Practice':
                option = self.choose_exercise()
                while(True):                    
                    if option == 'Translate Target to English':
                        exercise = 'Forward Translate'
                    elif option == 'Translate English to Target':
                        exercise = 'Backward Translate'
                    else:
                        break
                    entry = self.question_handler.sample_question(exercise=exercise)
                    answer = self.get_answer(entry['question'])
                    result = self.question_handler.evaluate_answer(entry, answer, exercise)
                    value = self.display_question_results(entry['target'], result)
                    if value == 0:
                        break
            elif option == 'Show Scores':
                exercise = self.choose_exercise()
                print(exercise)
                if exercise == 'Back':
                    continue
            
            elif option == 'Settings':
                print('Wrong Choice')
            elif option == 'Exit':
                self.quit()
            