import pygame
import json, os
import time
import sys

from typing import Iterable, Tuple, Optional

from modules.support_classes import SettingsHandler, DatabaseHandler

class TrainerApp:
    """ This class contains the main application that will handle the front-end, it will also control the back-end
         class (QuestionHandler)"""
   
    def __init__(self, resource_dir:str):
        self.resource_dir = resource_dir
        self.stg = SettingsHandler(resource_dir)

        self.resource_dir = resource_dir
        self.db_handler = DatabaseHandler(self.stg['Database'], self.stg['Excel Sheet'])

        self.status = 'reset'
        self.user_answer = ''
        self.target_area = (0, 0, 0, 0)
        
        img_size = self.stg['Screen Resolution']
        pygame.init()
        self.home_img = pygame.image.load(f'{resource_dir}/main_menu.jpg')
        self.home_img = pygame.transform.scale(self.home_img, img_size)


        self.bg = pygame.image.load(f'{resource_dir}/background.jpg')
        self.bg = pygame.transform.scale(self.bg, img_size)

        self.screen = pygame.display.set_mode(img_size, pygame.RESIZABLE)
        pygame.display.set_caption('Vocabulary Trainer')        

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
            self.handle_for_repeating_events(event)
            if event.type == pygame.MOUSEBUTTONUP:
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
        # Calculate rects for the question, answer, and target fields
        item_names = [question, self.user_answer, '']
        dims = {'rel_y':30, 'rel_x':15, 'rel_w':70, 'rel_h':15, 'rel_gap':6}
        items = self.calculate_rect_placements(item_names, dims)
        # draw the question
        self.draw_text(question, rect=items[0][1], bgcolor=(237,125,49))
        # This area will be used to display the correct answer later
        self.target_area = items[-1][1]
        
        while self.status == 'active':
    
            # update the text of user input
            self.draw_text(self.user_answer, rect=items[1][1], bgcolor=(237,125,49))
            
            for event in pygame.event.get():
                self.handle_for_repeating_events(event)
                if event.type == pygame.KEYDOWN:
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
                       

    def display_question_results(self, correct_answer:str, answered_correctly:bool, question_idx:int, direction:int)->Optional[int]:
        """
        Displays the results for a question on the screen
        :param correct_answer: the correct answer to the question, diplayed below the answer given by the user
        :param answered_correctly: whether the user answered the question correctly
        :param question_idx: the index of the question in the vocabulary database, to be used when the user wants to
         update the target
        :param direction: the direction of the exercise, to be used when updating or adding translations
        :returns: 0 if the escape key was pressed, 1 if "enter" or "space' where pressed
        """
        if answered_correctly:
            bgcolor = (0, 0, 255)
        else:
            bgcolor = (255, 0, 0)

        # update the text of user input
        self.draw_text(correct_answer, rect=self.target_area, bgcolor=bgcolor)

        # Collect rects for Edit Target, Add Alternative Translation and Delete Entry
        item_names = ['Edit Target', 'Add Alternative Translation', 'Delete Entry']
        dims = {'rel_y':92, 'rel_x':7.5, 'rel_w':25, 'rel_h':7, 'rel_gap':5}
        options = self.calculate_rect_placements(item_names, dims, horizontal=True)
        self.add_items_to_screen(options)

        while(True):
            event = pygame.event.wait()
            self.handle_for_repeating_events(event)
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_SPACE, pygame.K_RETURN] :
                return 1
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return 0
            elif event.type == pygame.MOUSEBUTTONUP:
                option = self.get_matching_area(options)
                if option == 'Add Alternative Translation' and not correct_answer:
                    self.db_handler.add_alternative_translation(question_idx, self.user_answer, direction)
                elif option == 'Delete Entry':
                    self.db_handler.delete_entry(question_idx)
                elif option == 'Edit Target':
                    new_target = self.edit_target(correct_answer)
                    self.db_handler.set_translation_target(question_idx, correct_answer, new_target)
                    self.draw_text(new_target, rect=self.target_area, bgcolor=bgcolor)
    
    def edit_target(self, target):
        while True:
            self.draw_text(target, rect=self.target_area, bgcolor=(237,125,49))
            for event in pygame.event.get():
                    self.handle_for_repeating_events(event)
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_BACKSPACE:
                            target = target[:-1]
                        elif event.key == pygame.K_RETURN:
                            return target
                        else:
                            try:
                                target += event.unicode
                            except:
                                pass
    
    def reset_screen(self, image):
        """
        Resets a given screen by displaying a new background image
        :param image: the image to display

        """
        app_size = self.stg['Screen Resolution']
        if image.get_size() != app_size:
            self.home_img = pygame.transform.scale(image, app_size)
        self.screen.blit(image, (0,0))
        pygame.display.update()
    
    def handle_for_repeating_events(self, event):
        ''' Monitors if the user wants to exist or resized the window.
            :returns: True if the event was resizing, else False
        '''
        if event.type == pygame.QUIT:
            self.quit()
        if event.type == pygame.VIDEORESIZE:
            self.stg['Screen Resolution'] = (event.w, event.h)
            return True
        return False
            
    def quit(self):
        """ Performs the necessary actions before the application exits"""
        self.db_handler.save_database(self.stg['Database'], self.stg['Excel Sheet'])
        self.stg.save_settings()
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
                        single_query = True
                    elif option == 'Translate English to Target':
                        exercise = 'Backward Translate'
                        single_query = False
                    else:
                        break
                    entry = self.db_handler.sample_question(exercise, single_query)
                    answer = self.get_answer(entry['question'])
                    result = self.db_handler.evaluate_answer(entry, answer, exercise)
                    direction = exercise.split()[0]
                    value = self.display_question_results(entry['target'], result, entry['ID'], direction)
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
    
    def calculate_rect_placements(self, item_names:Iterable[str], dimensions:dict, horizontal:bool=False)->tuple:
        """
        Calculates equidistant placements for objects on a screen
        :param item_names: a list of strings containing the name of the items to be added
         to assign a type to an item you could add it after a '.', e.g. "Start.TextArea"
        :params dimensions: dictionary contining the rel (in %) dimensions of the items
         it should contain the following keys: 
         - rel_y: the starting y relative to the height
         - rel_x: the starting x relative to the width
         - rel_w and rel_h: relative heights and widths of each item
         - rel_gap: the gap between two item
        :params horizontal: if true, the items are placed horizontally (right-to-left) else
         the items are placed vertically (top-to-bottom)
        :returns: a list of tuple with each element as follows (item_name, item_rect, item_type)
        """
        w, h = self.stg['Screen Resolution']
        # Divide by 100 each dimension
        dimensions = {x:y/100 for x, y in dimensions.items()}
        current_y = int(dimensions['rel_y']*h)
        current_x = int(dimensions['rel_x']*w)
        width, height = int(dimensions['rel_w']*w), int(dimensions['rel_h']*h)
        # Calculate the gaps between the start of two items (vertical and horizontal)
        gap_v = int(dimensions['rel_gap']*h) + height if not horizontal else 0
        gap_h = int(dimensions['rel_gap']*w) + width if horizontal else 0
        output = []
        for item in item_names:
            item += '.' # To account for when the type isn't added
            name, item_type = tuple(item.split('.'))[:2]
            output.append((name, (current_x, current_y, width, height), item_type))
            current_y += gap_v
            current_x += gap_h
        return output
    
    def add_items_to_screen(self, items:Iterable[str], fgcolor=(19, 161, 14), bgcolor=(255, 255, 255))->None:
        """
        Adds a list of items to a screen
        :param items: a list of strings containing the name of the items, each element should
         have the following form (name, (x, y, w, h), type), an empty type is treated as a rectangle
        :param fgcolor: the color of the forground (text)
        :param bgcolor: the color of the background
        :returns: a list of tuple with each element as follows (item_name, item_rect)
        """
        for item in items:
            fsize = item[1][3]//2 # The font size will be half the rectangle height
            self.draw_text(item[0], rect=item[1], fsize=fsize, fgcolor=fgcolor, bgcolor=bgcolor)
