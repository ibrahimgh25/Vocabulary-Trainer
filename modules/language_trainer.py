import numpy as np

from .trainer_utils import guess_word
from .utils import normalize_weights
from .excel_ops import get_excel_df, save_to_excel


class LanguageTrainer():
    def __init__(self, excel_file, sheet_name):
        self.lang_df = get_excel_df(excel_file, sheet_name)
        # define a private attribute to store the direction
        # of the training session
        self.__direction = 'Backward'
    
    def training_session(self):
        ''' Do a training session '''
        indices = list(range(len(self.lang_df)))
        go_again = True
        while(go_again):
            draw = np.random.choice(indices, p=normalize_weights(self.lang_df[self.__direction]))
            entry = self.lang_df.iloc[draw].to_dict()
            result = guess_word(entry, self.__direction)
            if result:
                self.lang_df.loc[self.lang_df.index==draw, self.__direction] += 1
                self.lang_df.loc[self.lang_df.index==draw, self.__direction] = max(0, self.lang_df.iloc[draw][self.__direction])
            elif result == False:
                self.lang_df.loc[self.lang_df.index==draw, self.__direction] -= 1
            else:
                go_again = False
        print('Session finished.')
    
    def set_direction(self, direction):
        ''' Set the direction of the training session '''
        assert direction in ['Forward', 'Backward'], 'Direction must be "Forward" or "Backward"'
        self.__direction = direction
    

    def save_database(self, excel_file, sheet_name):
        ''' Save the database to an excel file '''
        save_to_excel(self.lang_df, excel_file, sheet_name)