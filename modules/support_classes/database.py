import re
import shutil, os, datetime
import warnings

import numpy as np

from typing import Iterable, Tuple, Union, Any
from ..utils import ( 
                    generate_id, 
                    sample_entry, 
                    add_special_chars,
                    matching)
from ..utils.excel_ops import get_excel_df, save_to_excel

from .scores import ScoresHandler

class DatabaseHandler:
    """ This class handles loading, saving, and sampling from the database of vocabulary"""
    def __init__(self, excel_file, sheet_name):
        self.lang_df = None
        self.load_df(excel_file, sheet_name)
        self.loaded_sheet = sheet_name
        # define a private attribute to store the direction
        # of the training session
        
        # Define the available for IDs
        self.used_ids = self.lang_df['ID'].tolist()


    def load_df(self, excel_file:str, sheet_name:str) -> None:
        """
        Loads the dataframe containing the vocabulary to be used
        :param Excel_file: the path to the Excel file
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
    

    def save_database(self, excel_file:Union[str, os.PathLike], sheet_name:str, save_scores:bool=True) -> None:
        """
        Save the database to an Excel file
        :param Excel_file: the name of the Excel file
        :param sheet_name: the sheet name used for saving
        :param save_scores: if True the scores from "self.scores" will be saved too
        """
        self.backup_database(excel_file, True)
        save_to_excel(self.lang_df, excel_file, sheet_name)

    def backup_database(self, excel_file:Union[str, os.PathLike], add_timestamp:bool=True):
        """
        Backup the database to a backup path
        :param Excel_file:
        :param add_timestamp:  (Default value = True)
        """
        # Copy the database to a backup file
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
        Formulate the translation question and answer for a database row
        :param entry: dictionary created from the database row
        :param direction: the direction of translation
        :returns: a tuple containing the question and the target
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
    
    
    def get_matching_indices(self, category:str) -> Iterable[int]:
        """
        Returns the indices of rows matching a specific category
        :param category: string containing the category used for filtering
        :returns: the list of matching indices
        """
        categories = self.lang_df['Category'].unique()
        categories = [x for x in categories if category in x]
        indices = self.lang_df[self.lang_df['Category'].isin(categories)].index
        return indices
    
    def add_alternative_translation(self, entry_id:int, translation:str, direction:str):
        """ Add an alternative translation to specific word
            :param entry_id: the id of the entry in the database
            :param translation: the alternative translation to add
            :param direction: the direction of the translation
        """
        idx = np.where(self.lang_df['ID'].values==entry_id)[0][0]
        assert direction in ['Forward', 'Backward']
        column = f'Alternative {direction}'
        if ';' in translation or ',' in translation:
            warnings.warn(f'{translation} contains an invalid character, ignoring the command')
            return False
        # If there's already an alternative translation separate the new entry with a ';'
        if self.lang_df[column].values[idx] != '':
            self.lang_df.loc[self.lang_df.index==idx, column] += ';' + translation
        else:
            self.lang_df.loc[self.lang_df.index==idx, column] = translation
        return True
    
    def delete_entry(self, entry_id:int):
        """ Delete a specific entry in the database"""

        idx = np.where(self.lang_df['ID'].values==entry_id)[0][0]
        self.lang_df.drop(int(idx), axis=0, inplace=True)

        self.used_ids = self.lang_df['ID'].values
        
    def set_translation_target(self, entry_id:int, old_target:str, new_target:str):
        """ Change the translation target of an entry
            :param entry_id: the id of the entry
            :param old_target: the old translation target (to determine which fields to change
            :param new_target: the new translation target (to replace the old one)
        """
        idx = np.where(self.lang_df['ID'].values==entry_id)[0][0]
        entry = self.lang_df.loc[idx].to_dict()
        for key, value in entry.items():
            if value == old_target:
                self.lang_df.loc[self.lang_df.index==idx, key] = new_target
    
    def apply_filter(self, exercise:str, n_samples:int=0, included_categories:Iterable[str]=[], excluded_categories:Iterable[str]=[]):
        """ Apply a filter to the available questions
            :param exercise: the name of the exercise to use for getting the weights when sampling
            :param n_samples: the number of samples to be set in the final filtering
            :param included_categories: the categories to be sampled in (white filter)
            :param excluded_categories: the categories to be sampled out (black filter)
        """
        df = self.lang_df # Just to have a shorter code
        self.used_ids = df['ID'].values

        matches_category = lambda x, category: category in df.loc[df['ID']==x, 'Category'].values[0]
        # Exclude the categories in excluded categories
        for cat in excluded_categories:
            self.used_ids = [x for x in self.used_ids if not matches_category(x, cat)]
        # Include only the categories in included_categories
        for cat in included_categories:
            self.used_ids = [x for x in self.used_ids if matches_category(x, cat)]
        # Sample the needed number of words
        if n_samples > len(df) or n_samples <= 0:
            sampled_entries = df.sample(len(df), replace=False)
        elif n_samples > 0:
            sampled_entries = df.sample(n=n_samples, replace=False)

        self.used_ids = sampled_entries.loc[:, 'ID'].tolist()

    def get_scores_summary(self, scores):
        """ Return the score summary for a particular exercise"""
        summary = scores.summarize()
        # Replace the ids by their names
        ids = self.lang_df['ID'].values
        for key in ['max', 'min']:
            element_id = int(summary[key][0])
            idx = np.where(ids==element_id)[0][0]
            summary[key][0] = self.lang_df.loc[self.lang_df.index==idx, 'Word_s'].values[0]
        # Round the average score to two decimal points
        summary['average'] = round(summary['average'], 2)
        return summary

    def get_scores_path(self, exercise):
         direction = exercise.split()[-1]
         exercise_type = exercise.split()[0]
         return f'{exercise_type}_{self.loaded_sheet}_{direction}.json'

    def sample_random_entry(self, ids, weights) -> dict[str, str | Any] | list[
        dict[str, str | Any]]:
        """
        Sample a question for a specific exercise
        :param ids: the ids to sample from
        :param weights: the weights to assign for each id (should match ids size)
        :returns: the sampled row as a dictionary
        """
        draw = np.random.choice(ids, p=weights)

        available_ids = self.lang_df['ID'].values
        indices = [np.where(available_ids==draw)[0][0]]
        entries = [self.lang_df.loc[idx].to_dict() for idx in indices]
        return entries[0]