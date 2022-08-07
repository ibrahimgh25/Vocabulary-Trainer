from turtle import bgcolor
import pygame

import time

    
class TrainerInterface:
   
    def __init__(self, resource_dir):
        self.size = (750, 500)
        self.w, self.h = self.size

        self.head_color = (255,213,102)
        self.text_color = (240,240,240)

        self.status = 'reset'
        self.user_answer = ''
        
       
        pygame.init()
        self.open_img = pygame.image.load(f'{resource_dir}/main_menu.jpg')
        self.open_img = pygame.transform.scale(self.open_img, self.size)


        self.bg = pygame.image.load(f'{resource_dir}/background.jpg')
        self.bg = pygame.transform.scale(self.bg, self.size)

        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption('Vocabulary Trainer')
          
    def draw_text(self, msg, y , rect,  fgcolor=(255, 255, 255), fsize=26, bgcolor=(0, 0, 0)):
        self.screen.fill(bgcolor, rect)
        pygame.draw.rect(self.screen, bgcolor, rect, 2)
        
        font = pygame.font.Font(None, fsize)
        text = font.render(msg, 1,fgcolor)
        center = (rect[0] + rect[2]//2, rect[1] + rect[3]//2)
        text_rect = text.get_rect(center=center)
        self.screen.blit(text, text_rect)
        pygame.display.update()   
    
    def add_options(self, options):
        current_y = int(0.29*self.h) # Start from y 29% from total height
        start_x = int(0.05*self.w) # Start from x 5% from total width
        width = int(0.35*self.w) # Width of 35%
        height = int(0.1*self.h)
        gap = int(0.016*self.h) # Distance between two options
        fsize = height//2
        output = []
        fcolor = (19, 161, 14)
        bgcolor = (255, 255, 255, 0)
        for option in options:
            output.append((option, (start_x, current_y, width, height)))
            self.draw_text(option, y=current_y+fsize/4, rect=output[-1][1], fsize=fsize, fgcolor=fcolor, bgcolor=bgcolor)
            current_y += gap + height
        return output
        
    def start(self):
        self.reset_screen(self.open_img)
        self.status = 'idle'
        pygame.display.update()
        
        options = ['Translate English to Target',
                    'Translate Target to English',
                    'Settings',
                    'Exit'
                    ]
        options = self.add_options(options)
        while(True):
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                self.status = 'dead'
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONUP:
                matching_area = self.get_matching_area(options)
                if matching_area not in ['Settings', 'Exit']:
                    return matching_area
     
    def get_matching_area(self, options):
        x, y = pygame.mouse.get_pos()
        for option in options:
            rect = option[1]
            matching_x = x > rect[0] and x < rect[0] + rect[2]
            matching_y = y > rect[1] and y < rect[1] + rect[3]
            if matching_x and matching_y:
                return option[0]
        return ''
        
    def get_answer(self, question):
        self.status = 'active'
        self.user_answer = ''
        self.reset_screen(self.bg)
        # draw the question
        self.draw_text(question, y=200, rect=(50,180,650,50), bgcolor=(237,125,49))
        while self.status == 'active':
    
            # update the text of user input
            self.draw_text(self.user_answer, y=274, rect=(50,250,650,50), bgcolor=(237,125,49))
            
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
                       

    def display_question_results(self, correct_answer, answered_correctly):
        if answered_correctly:
            bgcolor = (0, 0, 255)
        else:
            bgcolor = (255, 0, 0)

        # update the text of user input
        self.draw_text(correct_answer, y=360 ,rect=(50, 340, 650, 50), bgcolor=bgcolor)

        while(True):
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                self.status = 'dead'
                pygame.quit()
                return 0
            elif event.type == pygame.KEYDOWN and event.key in [pygame.K_SPACE, pygame.K_RETURN] :
                return 1
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return 0
    
    def reset_screen(self, image):
        self.screen.blit(image, (0,0))
        pygame.display.update()