import shutil, os, datetime
import numpy as np

from .trainer_utils import guess_word
from .utils import normalize_weights
from .excel_ops import get_excel_df, save_to_excel


class LanguageTrainer():
    def __init__(self, excel_file, sheet_name):
        self.lang_df = get_excel_df(excel_file, sheet_name)
        # self.adjust_id_column()
        # define a private attribute to store the direction
        # of the training session
        self.__direction = 'Backward'
    
    def translation_session(self, category=''):
        ''' Do a training session '''
        # group accordign to category
        indices = self.get_matching_indices(category)
        score_col = self.__direction
        while(True):
            scores = self.lang_df.loc[indices, score_col].values
            draw = np.random.choice(indices, p=normalize_weights(scores))
            entry = self.lang_df.loc[draw].to_dict()
            result = guess_word(entry, score_col)
            if result:
                self.lang_df.loc[draw, score_col] += 1
                # set the row to a zero if it's still negative
                self.lang_df.loc[self.lang_df.index==draw, score_col] = max(0, self.lang_df.iloc[draw][score_col])
            elif result == False:
                self.lang_df.loc[draw, score_col] -= 1
            else:
                # if the result is None, the test ends
                break
        print('Session finished.')
    
    def set_direction(self, direction):
        ''' Set the direction of the training session '''
        assert direction in ['Forward', 'Backward'], 'Direction must be "Forward" or "Backward"'
        self.__direction = direction
    

    def save_database(self, excel_file, sheet_name):
        ''' Save the database to an excel file '''
        save_to_excel(self.lang_df, excel_file, sheet_name)
    
    def get_matching_indices(self, category):
        ''' Return a list of indices that match a given category '''
        categories = self.lang_df['Category'].unique()
        categories = [x for x in categories if category in x]
        indices = self.lang_df[self.lang_df['Category'].isin(categories)].index
        return indices

    def backup_database(self, excel_file, add_timestamp=True):
        ''' Backup the database to a backup path '''
        # Copy the database to a backup file
        back_up_path = excel_file.replace('.xlsx', '_backup.xlsx')
        file_name = os.path.basename(excel_file)

        if add_timestamp:
            # Add a stamp at the start of the file name
            stamp = str(datetime.datetime.now()).replace(':', '-') + '_'            
            back_up_path = os.path.join('backup', stamp + file_name)
        else:
            back_up_path = os.path.join('backup', file_name)
        # Create the backup directory if it doesn't exist
        if not os.path.exists('backup'):
            os.mkdir('backup')
        shutil.copy(excel_file, back_up_path)