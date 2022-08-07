import shutil, os, datetime
import json
import numpy as np

from .utils import normalize_weights, generate_id, sample_entry, add_special_chars
from .excel_ops import get_excel_df, save_to_excel
from .trainer_utils import matching
from .pygame_interface import TrainerInterface

class LanguageTrainer():
    def __init__(self, excel_file, sheet_name, gui_resource_dir):
        self.load_df(excel_file, sheet_name)
        # define a private attribute to store the direction
        # of the training session
        self.__direction = 'Backward'
        if not os.path.exists('resources/scores'):
            os.mkdir('resources/scores')
        self.app = TrainerInterface(gui_resource_dir)
    
    def load_df(self, excel_file, sheet_name):
        self.loaded_sheet = sheet_name
        self.loaded_file = excel_file

        self.lang_df = get_excel_df(excel_file, sheet_name)
        # Take care of the ID column
        if not 'ID' in self.lang_df.columns:
            self.lang_df.insert(loc=0, column='ID', value=0)
        self.lang_df['ID'].fillna(0, inplace=True)
        id_digits = 8
        for idx, word_id in enumerate(self.lang_df['ID'].values):
            if word_id=='' or word_id < 10**(id_digits-1):
                self.lang_df.loc[self.lang_df.index==idx, 'ID'] = generate_id(id_digits, self.lang_df['ID'])
    
    def translation_session(self, category=''):
        ''' Do a training session '''
        # group accordign to category
        indices = self.get_matching_indices(category)
        scores = self.load_scores('translate', self.loaded_sheet, self.__direction)
        while(True):
            draw = np.random.choice(indices, p=normalize_weights(list(scores.values())))
            entry = self.lang_df.loc[draw].to_dict()
            result, target = self.guess_word(entry)
            id = str(self.lang_df.loc[draw, 'ID'])
            exit = self.app.display_question_results(target, result)
            if result:
                scores[id] += 1
                # set the row to a zero if it's still negative
                scores[id] = max(0, scores[id])
            elif result == False:
                scores[id] -= 1
            else:
                # if the result is None, the test ends
                # We should save the new scores
                self.save_scores(scores, 'translate', self.loaded_sheet, self.__direction)
                break
            if exit == 0:
                self.save_scores(scores, 'translate', self.loaded_sheet, self.__direction)
                break
        print('Session finished.')
    
    def load_scores(self, *args):
        ''' Load the scores for a particular task'''
        score_path = 'resources/scores/' + '_'.join([*args]) + '.json'
        try:
            scores = json.load(open(score_path, 'r'))
        except:
            scores = {}
            print(score_path)
        # Fill in for the new IDs that still have no entry in the score
        for id in self.lang_df['ID']:
            if not str(id) in scores.keys():
                scores[id] = 0
        return scores
    
    def save_scores(self, scores, *args):
        ''' Save the scores for a particular task'''
        score_path = 'resources/scores/' + '_'.join([*args]) + '.json'
        json.dump(scores, open(score_path, 'w'))

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
    
    def main_loop(self):
        option = self.app.start()
        if option == 'Translate English to Target':
            self.__direction = 'Backward'
            self.translation_session()
        elif option == 'Translate Target to English':
            self.__direction = 'Forward'
            self.translation_session()
        else:
            print('Wrong choice!')
        self.save_database(self.loaded_file, self.loaded_sheet)
    
    def guess_word(self, entry):
        target_keys = ['Translation', 'Translation_f']
        query_keys = ['Word_s', 'Word_p', 'Word_fs', 'Word_fp']
        if self.__direction == 'Backward':
            target_keys, query_keys = query_keys, target_keys
        elif not self.__direction=='Forward':
            raise ValueError('Direction must be "Forward" or "Backward"')
        
        target, target_key = sample_entry(entry, target_keys)
        if '_f' in target_key:
            query_keys = [x for x in query_keys if '_f' in x]
        else:
            query_keys = [x for x in query_keys if not '_f' in x]
        query, query_key = sample_entry(entry, query_keys)
        if self.__direction == 'Backward' and target_key != '':
            query = query + ' (' + target_key.split('_')[-1] + ')'
        answer = self.app.get_answer(query)
        answer = add_special_chars(answer)
        if matching(answer, target):
            return True, target
        elif answer == 'exit()':
            return None, target
        else:
            return False, target