import re
import shutil, os, datetime
import json, warnings
from modules.support_classes.scores import ScoresHandler


import numpy as np

from typing import Iterable, Tuple, Union
from ..utils import ( 
                    generate_id, 
                    sample_entry, 
                    add_special_chars,
                    matching)
from ..utils.excel_ops import get_excel_df, save_to_excel

from .scores import ScoresHandler

class DatabaseHandler():
    """ This class handles loading, saving, and sampling from the database of vocabulary"""
    def __init__(self, excel_file, sheet_name):
        self.load_df(excel_file, sheet_name)
        # define a private attribute to store the direction
        # of the training session
        
        # Define the avialable for IDs
        self.used_ids = self.lang_df['ID'].values

        # Define the ScoreHandler instance
        self.scores = ScoresHandler(sheet_name, self.used_ids)

    def load_df(self, excel_file:str, sheet_name:str) -> None:
        """
        Loads the dataframe contianing the vocabulary to be used
        :param excel_file: the path to the excel file
        :param sheet_name: the name of the sheet containing the data
        """
        self.lang_df = get_excel_df(excel_file, sheet_name)
        # Take care of the ID column
        if not 'ID' in self.lang_df.columns:
            self.lang_df.insert(loc=0, column='ID', value=0)
        self.lang_df['ID'].fillna(0, inplace=True)
        id_digits = 8
        for idx, word_id in enumerate(self.lang_df['ID'].values):
            if word_id=='' or word_id < 10**(id_digits-1):
                self.lang_df.loc[self.lang_df.index==idx, 'ID'] = generate_id(id_digits, self.lang_df['ID'])
    
    def evaluate_answer(self, entry:dict, answer:str, exercise:str) -> bool:
        """
        Evaluates an answer by matching it with the entry and updates the scores
        :param entry: a dictionary containing information about the question, it 
         has the following form {'target':target, 'ID':id, 'question':question}
        :param answer: the user answer
        :param exercise: the name of the exercise (will be used to access the scores)
        :returns: True if the answer is right False otherwise
        Note: the function automtically updates the scores using the ID in entry and the
         exercise name
        """
        # Handle for special characters that you're too lazy to type (like: Ö)
        answer = add_special_chars(answer)
        
        target = entry['target']
        result = matching(answer, target)
        # Update the scores
        self.scores.update(entry['ID'], exercise, result)
        return result
            
    
    def sample_question(self, exercise:str, single_query:bool=False) -> dict:
        """
        Sample a question for a specific exercise
        :param exercise: the name of the exercise
        :param single_query: if True, a single word is arbitrary chosen as the question, e.g.,
         instead of "nice, beautiful, pretty" the question could be "pretty"
        :returns: a dictionary with the following form:
         {'question':question_text, 'ID':id, 'target':target}
        """
        # Get the weights to use in the drawing process
        weights = self.scores.get_weights(exercise, self.used_ids)
        draw = np.random.choice(self.used_ids, p=weights)
        idx = np.where(self.used_ids==draw)[0][0]
        entry = self.lang_df.loc[idx].to_dict()
        # RENAME THIS
        query, target = self.formulate_translation_question(entry, exercise.split()[0])
        # If a single query is required, remove the paranthesis and choose a random word
        # for asking
        if single_query:
            query = re.sub(r'\([^)]*\)', '', query)
            query = np.random.choice(re.split(',|;', query)).strip()

        return {'question':query, 'ID':entry['ID'], 'target':target}

    def save_database(self, excel_file:Union[str, os.PathLike], sheet_name:str, save_scores:bool=True) -> None:
        """Save the database to an excel file

        :param excel_file: the name of the excel file
        :param sheet_name: the sheet name used for saving
        :param save_scores: if True the scores in self.scores will be saved too
        """
        save_to_excel(self.lang_df, excel_file, sheet_name)
        if save_scores:
            self.scores.save_all_scores()
    
    def get_matching_indices(self, category:str) -> Iterable[int]:
        """
        Returns the indices of rows matching a specific category
        :param category: string contianing the category used for filtering
        :returns: the list of mathcing indices
        """
        categories = self.lang_df['Category'].unique()
        categories = [x for x in categories if category in x]
        indices = self.lang_df[self.lang_df['Category'].isin(categories)].index
        return indices

    def backup_database(self, excel_file:Union[str, os.PathLike], add_timestamp:bool=True):
        """Backup the database to a backup path

        :param excel_file: 
        :param add_timestamp:  (Default value = True)

        """
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
    
    
    def formulate_translation_question(self, entry:dict, direction:str)->Tuple[str, str]:
        """
        Formulatest the translation question and answer for a database row
        :param entry: dictionary created from the database row
        :param direction: the direction of translation
        :returns: a tuple contianing the question and the target
        """
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
    
    def add_alternative_translation(self, id:int, translation:str, direction:str):
        ''' Add an alternative translation to specific word
            :param id: the id of the entry in the database
            :param translation: the alternative translation to add
            :param direction: the direction of the translation
        '''
        idx = np.where(self.used_ids==id)[0][0]
        assert direction in ['Forward', 'Backward']
        column = f'Alternative {direction}'
        if ';' in translation or ',' in translation:
            warnings.warn(f'{translation} contains an invalid character, ingoring the command')
            return False
        # If there's already an alternative translation separate the new entry with a ';'
        if self.lang_df[column].values[idx] != '':
            self.lang_df.loc[self.lang_df.index==idx, column] += ';' + translation
        else:
            self.lang_df.loc[self.lang_df.index==idx, column] = translation
        return True
    
    def delete_entry(self, entry_id:int):
        ''' Delete a specific entry in the database'''
        # Delete the score for that entry too
        self.scores.remove_id(entry_id)

        idx = np.where(self.used_ids==entry_id)[0][0]
        self.lang_df.drop(int(idx), axis=0, inplace=True)

        self.used_ids = self.lang_df['ID'].values
        
    def set_translation_target(self, idx:int, old_target:str, new_target:str):
        ''' Change the translation target of an entry
            :param ids: the id of the entry
            :param old_target: the old translation target (to determine which fields to change
            :param new_target: the new translation target (to replace the old one)
        '''
        idx = np.where(self.used_ids==idx)[0][0]
        entry = self.lang_df.loc[idx].to_dict()
        for key, value in entry.items():
            if value == old_target:
                self.lang_df.loc[self.lang_df.index==idx, key] = new_target
    
    def apply_filter(self, categories='', top_n=None):
        pass

    def get_scores_summary(self, exercise):
        summary = self.scores.summarize(exercise)
        # Replace the ids by their names
        for key in ['max', 'min']:
            element_id = int(summary[key][0])
            idx = np.where(self.used_ids==element_id)[0][0]
            summary[key][0] = self.lang_df.loc[self.lang_df.index==idx, 'Word_s'].values[0]
        # Round the average score to two decimal points
        summary['average'] = round(summary['average'], 2)
        return summary