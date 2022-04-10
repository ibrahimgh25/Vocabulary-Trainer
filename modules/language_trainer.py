import numpy as np

from .trainer_utils import guess_word
from .utils import normalize_weights
from .excel_ops import get_excel_df, save_to_excel


class LanguageTrainer():
    def __init__(self, excel_file, sheet_name):
        self.lang_df = get_excel_df(excel_file, sheet_name)
        self.adjust_id_column()
        # define a private attribute to store the direction
        # of the training session
        self.__direction = 'Backward'
    
    def translation_session(self, category=''):
        ''' Do a training session '''
        # group accordign to category
        categories = self.lang_df['Category'].unique()
        categories = self.get_matchin_cats(categories, category)
        training_df = self.lang_df[self.lang_df['Category'].isin(categories)]
        
        indices = list(range(len(training_df)))
        go_again = True
        while(go_again):
            draw = np.random.choice(indices, p=normalize_weights(training_df[self.__direction]))
            entry = training_df.iloc[draw].to_dict()
            result = guess_word(entry, self.__direction)
            if result:
                training_df.loc[training_df.index==draw, self.__direction] += 1
                # set the row to a zero if it's still negative
                training_df.loc[training_df.index==draw, self.__direction] = max(0, training_df.iloc[draw][self.__direction])
            elif result == False:
                training_df.loc[training_df.index==draw, self.__direction] -= 1
            else:
                go_again = False
        self.copy_changes_to_original_df(training_df)
        print('Session finished.')
    
    def set_direction(self, direction):
        ''' Set the direction of the training session '''
        assert direction in ['Forward', 'Backward'], 'Direction must be "Forward" or "Backward"'
        self.__direction = direction
    

    def save_database(self, excel_file, sheet_name):
        ''' Save the database to an excel file '''
        save_to_excel(self.lang_df, excel_file, sheet_name)
    
    def get_matchin_cats(self, categories, category):
        ''' Return a list of categories that match the given category '''
        if category == '':
            return categories
        else:
            return [x for x in categories if category in x]
    
    def adjust_id_column(self):
        ''' Adjust the id column to start from 1 '''
        # Add an ID column as the first column if it doesn't exist
        if 'ID' not in self.lang_df.columns:
            self.lang_df.insert(0, 'ID', range(1, len(self.lang_df)+1))
        else:
            # Fill empty rows with the next available ID
            self.lang_df['ID'] = self.lang_df['ID'].fillna(method='ffill')
            print(self.lang_df.columns, 'Halalooya!')

    def copy_changes_to_original_df(self, training_df):
        ''' Copy the changes to the original dataframe '''
        training_df.loc[0, self.__direction] = 100
        print(training_df.head())
        self.lang_df.to_clipboard()
        # Copy the training_df "direction" column to the original df where the ID matches
        self.lang_df.loc[self.lang_df['ID'].isin(training_df['ID']), self.__direction] = training_df[self.__direction]
        print(self.lang_df.head())