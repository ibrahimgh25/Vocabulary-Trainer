import pygame
import sys, io
import matplotlib.pyplot as plt

from PIL import Image
from typing import List, Tuple, Optional

from .support_classes import SettingsHandler, DatabaseHandler
from .utils import rel2abs, detect_language
from .exercises import TranslationExercise


def get_matching_area(options:List[Tuple]):
    """
    calculates which option a mouse click matches
    :param options: a list of tuples representing all the options in the page, has the form [(option_name, option_rect), ...]
    :returns: name of the matched option, if no option was matched it returns ''
    """
    x, y = pygame.mouse.get_pos()
    for option in options:
        rect = option[1]
        matching_x = rect[0] < x < rect[0] + rect[2]
        matching_y = rect[1] < y < rect[1] + rect[3]
        if matching_x and matching_y:
            return option[0]
    return ''


class TrainerApp:
    """ This class contains the main application that will handle the front-end, it will also control the back-end
         class (QuestionHandler)"""
   
    def __init__(self, resource_dir:str, mode='practice'):
        self.resource_dir = resource_dir
        self.stg = SettingsHandler(resource_dir)

        self.resource_dir = resource_dir
        self.db_handler = DatabaseHandler(self.stg['Database'], self.stg['Excel Sheet'])

        self.status = 'reset'
        self.user_answer = ''
        self.target_area = (0, 0, 0, 0)
        # Detect the target and source languages, so they can be used in the exercise names
        print(self.db_handler.active_df.head())
        self.target_lang = detect_language(self.db_handler.active_df['Word_s'])
        self.source_lang = detect_language(self.db_handler.active_df['Translation'])
        # A dictionary to map the option name with the corresponding exercise
        self.exercises = {
            f'Translate {self.target_lang} to {self.source_lang}':'Forward Translate',
            f'Translate {self.source_lang} to {self.target_lang}':'Backward Translate',
            'Back':'Back'
            }

        pygame.init()
        self.home_img, self.bg = None, None

        self.screen = pygame.display.set_mode(self.stg['Screen Resolution'])
        self.load_images()

        pygame.display.set_caption('Vocabulary Trainer')

        # Apply the filtering
        # FIXME: apply change for when the sheet changes
        if self.stg.sample_length_varied() or self.stg.sheet_changed():
            included_cats = [x.strip() for x in self.stg['Included Categories'].split(',')]
            excluded_cats = [x.strip() for x in self.stg['Excluded Categories'].split(',')]
            n_samples = self.stg['Sample Size']
            self.db_handler.apply_filter('Forward Translate', n_samples, included_cats, excluded_cats)
            self.stg.set_sampled_words(self.db_handler.used_ids)
        elif len(self.stg['Sampled Words']) > 0:
            self.db_handler.used_ids = self.stg['Sampled Words']

        self.mode = mode
        self.quiz = None

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
        text = font.render(msg, True,fgcolor)
        center = (rect[0] + rect[2]//2, rect[1] + rect[3]//2)
        text_rect = text.get_rect(center=center)
        self.screen.blit(text, text_rect)
        pygame.display.update()   
    
    def add_options(self, options:List[str], dimensions:dict)->List[tuple]:
        """
        Add a list of options to a screen
        :param options: a list of strings containing the name of the options
        :param dimensions: dictionary containing the rel (in %) dimensions of the options
         it should contain the following keys: 
         - rel_y: the starting y relative to the height
         - rel_x: the starting x relative to the width
         - rel_w and rel_h: relative heights and widths of each option
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
    

    def load_images(self):
        """ Load and reshape the images used by the app"""
        img_size, resource_dir = self.stg['Screen Resolution'], self.resource_dir
        self.home_img = pygame.image.load(f'{resource_dir}/main_menu.jpg')
        self.home_img = pygame.transform.scale(self.home_img, img_size)


        self.bg = pygame.image.load(f'{resource_dir}/background.jpg')
        self.bg = pygame.transform.scale(self.bg, img_size)
        self.screen = pygame.display.set_mode(self.stg['Screen Resolution'])
    def start(self):
        """ This function displays the main menu until the user chooses a valid option
            :returns: the name of the pressed option
        """
        self.reset_screen(self.home_img)
        self.status = 'idle'
        pygame.display.update()
        
        options = ['Practice',
                    'Show Scores',
                    'Options',
                    'Exit'
                    ]
        dimensions = {'rel_y':29, 'rel_x':5, 'rel_w':35, 'rel_h':10, 'rel_gap':1.6}

        options = self.add_options(options, dimensions)
        return self.get_user_option(options)

    def choose_exercise(self):
        """ Choose an exercise to either display its score or practice it"""
        self.reset_screen(self.home_img)
        options = list(self.exercises.keys())
        dimensions = {'rel_y':29, 'rel_x':5, 'rel_w':35, 'rel_h':10, 'rel_gap':1.6}
        options = self.add_options(options, dimensions)
        chosen_option = self.get_user_option(options)
        return self.exercises[chosen_option]
        
    
    def get_user_option(self, options):
        """ Returns what option the user chooses on a given screen"""
        while True:
            event = pygame.event.wait()
            matching_area = self.handle_for_repeating_events(event, options=options)
            if matching_area and matching_area != '':
                return matching_area

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
        
        while True:
            # update the text of user input
            self.draw_text(self.user_answer, rect=items[1][1], bgcolor=(237,125,49))
            # TODO: If will still use this method, turn it into a function
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    return self.user_answer
                self.user_answer = self.handle_for_repeating_events(event, collected_text=self.user_answer)


    def display_question_results(self, correct_answer:str, answered_correctly:bool, question_idx:int, direction:str)->Optional[int]:
        """
        Displays the results for a question on the screen
        :param correct_answer: the correct answer to the question, displayed below the answer given by the user
        :param answered_correctly: whether the user answered the question correctly
        :param question_idx: the index of the question in the vocabulary database, to be used when the user wants to
         update the target
        :param direction: the direction of the exercise, to be used when updating or adding translations
        :returns: 0 if the escape key was pressed, 1 if "enter" or "space" where pressed
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

        while True:
            event = pygame.event.wait()
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_SPACE, pygame.K_RETURN] :
                return 1
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return 0
            option = self.handle_for_repeating_events(event, options=options)

            if option == 'Add Alternative Translation' and not answered_correctly:
                self.db_handler.add_alternative_translation(question_idx, self.user_answer, direction)
                self.draw_text(correct_answer, rect=self.target_area, bgcolor=(220, 220, 0))
            elif option == 'Delete Entry':
                self.db_handler.delete_entry(question_idx)
                self.quiz.set_sampled_ids(self.db_handler.used_ids)
                self.draw_text(correct_answer, rect=self.target_area, bgcolor=(0, 220, 220))
            elif option == 'Edit Target':
                new_target = self.edit_target(correct_answer)
                self.db_handler.set_translation_target(question_idx, correct_answer, new_target)
                self.draw_text(new_target, rect=self.target_area, bgcolor=bgcolor)
    
    def edit_target(self, target:str) -> str:
        while True:
            self.draw_text(target, rect=self.target_area, bgcolor=(237,125,49))
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    return target
                target = self.handle_for_repeating_events(event, collected_text=target)

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
    
    def handle_for_repeating_events(self, event,
                            collected_text: Optional[str] = None,
                            options: Optional[List] = None) -> Optional[str]:
        """
            Monitors if the user wants to exist or resized the window
            :param event: the event to be processed
            :param collected_text: if it's not None, we're assumed to be waiting a typing event, and the results
             are added to this string
            :param options: the list of available options
            :returns: if collected_text is not None, it returns the updated string after processing the event
             else if options is not None, it returns the name of the matching option
             else None is returned
        """
        if event.type == pygame.QUIT:
            self.quit()

        if collected_text is not None:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    collected_text = collected_text[:-1]
                else:
                    # TODO: The try block was removed as it didn't seem to do anything, make sure that's true
                    collected_text += event.unicode
            return collected_text

        if options is not None and event.type == pygame.MOUSEBUTTONUP:
            return get_matching_area(options)

    def quit(self):
        """ Performs the necessary actions before the application exits"""
        # This is to avoid saving every time the app is tested while developing
        if self.mode != 'testing':
            self.db_handler.save_database(self.stg['Database'])
            self.stg.save_settings()
        pygame.quit()
        sys.exit()
    
    def main_loop(self):
        """ The main loop of the application"""
        while True:
            option = self.start()
            if option == 'Practice':
                exercise = self.choose_exercise()
                if exercise == 'Back':
                    continue
                while True:
                    self.set_quiz(exercise)
                    entry = self.quiz.sample_question(self.db_handler)
                    answer = self.get_answer(entry['question'])
                    result = self.quiz.evaluate_answer(answer)

                    direction = exercise.split()[0]
                    value = self.display_question_results(entry['target'], result, entry['ID'], direction)
                    if value == 0:
                        self.quiz.__del__()
                        self.quiz = None
                        break
            elif option == 'Show Scores':
                exercise = self.choose_exercise()
                if exercise == 'Back':
                    continue
                else:
                    self.set_quiz(exercise)
                    self.show_scores_summary()
            
            elif option == 'Options':
                # This doesn't work for now
                self.stg.display_options(self.screen)
                self.load_images()

            elif option == 'Exit':
                self.quit()

    def set_quiz(self, exercise):
        direction = exercise.split()[0]
        scores_path = self.get_scores_path(exercise)
        self.quiz = TranslationExercise(scores_path, self.db_handler.used_ids, direction)

    def get_scores_path(self, exercise):
        return self.db_handler.get_scores_path(exercise)
    
    def calculate_rect_placements(self, item_names:List[str], dimensions:dict, horizontal:bool=False)->List[tuple]:
        """
        Calculates equidistant placements for objects on a screen
        :param item_names: a list of strings containing the name of the items to be added
         to assign a type to an item you could add it after a '|', e.g. "Start|TextArea"
        :param dimensions: dictionary containing the rel (in %) dimensions of the items
         it should contain the following keys: 
         - rel_y: the starting y relative to the height
         - rel_x: the starting x relative to the width
         - rel_w and rel_h: relative heights and widths of each item
         - rel_gap: the gap between two item
        :param horizontal: if true, the items are placed horizontally (right-to-left) else
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
            item += '|' # To account for when the type isn't added
            name, item_type = tuple(item.split('|'))[:2]
            output.append((name, (current_x, current_y, width, height), item_type))
            current_y += gap_v
            current_x += gap_h
        return output

    def add_items_to_screen(self, items:List[tuple], fgcolor=(19, 161, 14), bgcolor=(255, 255, 255))->None:
        """
        Adds a list of items to a screen
        :param items: a list of tuples containing the name of the items, each element should
         have the following form (name, (x, y, w, h), type), an empty type is treated as a rectangle
        :param fgcolor: the color of the foreground (text)
        :param bgcolor: the color of the background
        :returns: a list of tuple with each element as follows (item_name, item_rect)
        """
        for item in items:
            fsize = item[1][3]//2 # The font size will be half the rectangle height
            self.draw_text(item[0], rect=item[1], fsize=fsize, fgcolor=fgcolor, bgcolor=bgcolor)
    
    def show_scores_summary(self):
        """ Displays a page with a summary of the scores for a particular exercise"""
        # TODO: LATER SHOULD BE CHANGED TO A BETTER IMPLEMENTATION
        summary = self.db_handler.get_scores_summary(self.quiz.scores)
        self.screen.fill((0, 0, 0))
        screen_w, screen_h = self.stg['Screen Resolution']
        font = pygame.font.Font(None, int(0.1*screen_h/2))
        # FIXME: make this flexible
        exercise = "Translation Scores"
        # The title
        text = font.render(exercise, True, (19, 161, 14))
        text_rect = text.get_rect(center=(screen_w/2, screen_h/20))
        self.screen.blit(text, text_rect)
        # Calculate the rects of the different fields
        item_names = [
            f"Number of Entries: {summary['entries count']}",
            f"Worst Word: {summary['min'][0]}",
            f"Best Word: {summary['max'][0]}",
            f"Average Score: {format(summary['average'])}"
        ]
        dims = {'rel_y':15, 'rel_x':10, 'rel_w':80, 'rel_h':8, 'rel_gap':2}
        placements = self.calculate_rect_placements(item_names, dims)
        # Change the placements of the first and teh last element to be at the same vertical level
        x, frequencies, w, h = placements[0][1]
        placements[0] = (placements[0][0], [x, frequencies, int(0.45*w), h], '')
        placements[-1] = (placements[-1][0], [int(0.55*w) + x, frequencies, int(0.45*w), h], '')
        
        self.add_items_to_screen(placements)

        # Draw graph showing the distribution
        score = [x for x, _ in summary['distribution'].items()]
        frequencies = [y for _, y in summary['distribution'].items()]
        plt.clf()
        plt.bar(score, frequencies)

        plt.xticks(color='white')
        plt.yticks(color='white')
        plt.title('Scores Distribution')

        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png', facecolor=(0,0,0,0))

        ref = self.stg['Screen Resolution']
        rect = rel2abs([0.1, 0.4, 0.8, 0.55], ref)
        
        im = Image.open(img_buf)
        raw_str = im.tobytes("raw", 'RGBA')
        im = pygame.image.fromstring(raw_str, im.size, 'RGBA')
        
        im = pygame.transform.scale(im, rect[2:])
        self.screen.blit(im, rect[:2])
        pygame.display.update()
        while True:
            event = pygame.event.wait()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            elif event.type == pygame.QUIT:
                self.quit()