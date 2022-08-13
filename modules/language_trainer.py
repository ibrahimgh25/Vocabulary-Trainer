import shutil, os, datetime
import json
import numpy as np

from .utils import normalize_weights, generate_id, sample_entry, add_special_chars
from .excel_ops import get_excel_df, save_to_excel
from .trainer_utils import matching

class LanguageTrainer():
    def __init__(self, excel_file, sheet_name):
        self.load_df(excel_file, sheet_name)
        # define a private attribute to store the direction
        # of the training session
        
        if not os.path.exists('resources/scores'):
            os.mkdir('resources/scores')
        # Load the scores
        self.scores = {}
        self.scores['Forward Translate'] = self.load_scores('translate', sheet_name, 'Forward')
        self.scores['Backward Translate'] = self.load_scores('translate', sheet_name, 'Backward')

        # Define the avialable for IDs
        self.loaded_ids = self.lang_df['ID'].values

    def load_df(self, excel_file, sheet_name):
        self.lang_df = get_excel_df(excel_file, sheet_name)
        # Take care of the ID column
        if not 'ID' in self.lang_df.columns:
            self.lang_df.insert(loc=0, column='ID', value=0)
        self.lang_df['ID'].fillna(0, inplace=True)
        id_digits = 8
        for idx, word_id in enumerate(self.lang_df['ID'].values):
            if word_id=='' or word_id < 10**(id_digits-1):
                self.lang_df.loc[self.lang_df.index==idx, 'ID'] = generate_id(id_digits, self.lang_df['ID'])
    
    def evaluate_answer(self, entry, answer, exercise):
        answer = add_special_chars(answer)
        target = entry['target']
        result = matching(answer, target)

        id = str(entry['ID'])
        if result:
            self.scores[exercise]['scores'][id] += 1
            # set the row to a zero if it's still negative
            self.scores[exercise]['scores'][id] = max(0, self.scores[exercise]['scores'][id])
        elif result == False:
            self.scores[exercise]['scores'][id] -= 1
        return result
            
    
    def sample_question(self, exercise):
        # I know below is a lot of text, but bare with me
        weights = list(self.scores[exercise]['scores'].values())
        draw = np.random.choice(self.loaded_ids, p=normalize_weights(weights))
        idx = np.where(self.loaded_ids==draw)[0][0]
        entry = self.lang_df.loc[idx].to_dict()
        # RENAME THIS
        query, target = self.guess_word(entry, exercise.split()[0])
        return {'question':query, 'ID':entry['ID'], 'target':target}

    def load_scores(self, *args):
        ''' Load the scores for a particular task'''
        score_path = 'resources/scores/' + '_'.join([*args]) + '.json'
        try:
            scores = json.load(open(score_path, 'r'))
        except:
            scores = {}
        
        # Fill in for the new IDs that still have no entry in the score
        for id in self.lang_df['ID']:
            if not str(id) in scores.keys():
                scores[id] = 0
        return {'scores':scores, 'path':score_path}
    
    def save_scores(self, scores, *args):
        ''' Save the scores for a particular task'''
        score_path = 'resources/scores/' + '_'.join([*args]) + '.json'
        json.dump(scores, open(score_path, 'w'))

    def save_all_scores(self):
        for score in self.scores.values():
            json.dump(score, open(score['path'], 'w'))
    
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
    
    
    def guess_word(self, entry, direction):
        target_keys = ['Translation', 'Translation_f']
        query_keys = ['Word_s', 'Word_p', 'Word_fs', 'Word_fp']
        if direction == 'Backward':
            target_keys, query_keys = query_keys, target_keys
        elif not direction=='Forward':
            raise ValueError('Direction must be "Forward" or "Backward"')
        
        target, target_key = sample_entry(entry, target_keys)
        if '_f' in target_key:
            query_keys = [x for x in query_keys if '_f' in x]
        else:
            query_keys = [x for x in query_keys if not '_f' in x]
        query, query_key = sample_entry(entry, query_keys)
        if direction == 'Backward' and target_key != '':
            query = query + ' (' + target_key.split('_')[-1] + ')'
        return query, target