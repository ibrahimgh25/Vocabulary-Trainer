import re
import shutil, os, datetime
import warnings

import numpy as np

from typing import Iterable, Tuple, Union, Any

import pandas as pd

from ..utils import generate_id
from ..utils.excel_ops import get_excel_df, save_to_excel


class DatabaseHandler:
    """ This class handles loading, saving, and sampling from the database of vocabulary"""
    def __init__(self, excel_file, sheet_name):
        # define a private attribute to store the direction
        # of the training session
        
        self.database = {}
        self.load_all_sheets(excel_file)

        # Set the first dataframe as the active dataframe
        self.active_sheet = next(iter(self.database))
        self.active_df = self.database[self.active_sheet]
        self.used_ids = self.active_df['ID'].values

        # Now try to load the database with the following sheet name
        self.set_active_df(sheet_name)

    def set_active_df(self, sheet_name):
        # FIXME: Handle for when the sheetname isn't in the excel file (maybe just load the first sheet)
        self.active_df = self.database[sheet_name]
        self.used_ids = self.active_df['ID'].tolist()
        self.active_sheet = sheet_name

    def load_excel_sheet(self, excel_file, sheet_name) -> None:
        """
        Adds a dataframe loaded from an excel sheet to the database
        :param df: the dataframe containing the data
        :param sheet_name: the name of the sheet containing the data
        """
        df = get_excel_df(excel_file, sheet_name)
        # Take care of the ID column
        if not 'ID' in df.columns:
            df.insert(loc=0, column='ID', value=0)
        df['ID'].fillna(0, inplace=True)
        id_digits = 8
        for idx, word_id in enumerate(df['ID'].values):
            if word_id=='' or word_id < 10**(id_digits-1):
                df.loc[df.index==idx, 'ID'] = generate_id(id_digits, df['ID'])
        self.database[sheet_name] = df


    def save_database(self, excel_file:Union[str, os.PathLike]) -> None:
        """
        Save the database to an Excel file
        :param excel_file: the name of the Excel file
        """
        self.backup_excel_file(excel_file, True)
        for sheet_name, df in self.database.items():
            save_to_excel(df, excel_file, sheet_name)

    @staticmethod
    def backup_excel_file(excel_file:Union[str, os.PathLike], add_timestamp:bool=True):
        """
        Backup the database to a backup path
        :param excel_file: the excel file to backup
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
    
    
    def get_matching_indices(self, category:str) -> Iterable[int]:
        """
        Returns the indices of rows matching a specific category
        :param category: string containing the category used for filtering
        :returns: the list of matching indices
        """
        categories = self.active_df['Category'].unique()
        categories = [x for x in categories if category in x]
        indices = self.active_df[self.active_df['Category'].isin(categories)].index
        return indices
    
    def add_alternative_translation(self, entry_id:int, translation:str, direction:str):
        """ Add an alternative translation to specific word
            :param entry_id: the id of the entry in the database
            :param translation: the alternative translation to add
            :param direction: the direction of the translation
        """
        idx = np.where(self.active_df['ID'].values==entry_id)[0][0]
        assert direction in ['Forward', 'Backward']
        column = f'Alternative {direction}'
        if ';' in translation or ',' in translation:
            warnings.warn(f'{translation} contains an invalid character, ignoring the command')
            return False
        # If there's already an alternative translation separate the new entry with a ';'
        if self.active_df[column].values[idx] != '':
            self.active_df.loc[self.active_df.index==idx, column] += ';' + translation
        else:
            self.active_df.loc[self.active_df.index==idx, column] = translation
        return True
    
    def delete_entry(self, entry_id:int):
        """ Delete a specific entry in the database"""

        idx = np.where(self.active_df['ID'].values==entry_id)[0][0]
        self.active_df.drop(int(idx), axis=0, inplace=True)

        self.used_ids = self.active_df['ID'].values
        
    def set_translation_target(self, entry_id:int, old_target:str, new_target:str):
        """ Change the translation target of an entry
            :param entry_id: the id of the entry
            :param old_target: the old translation target (to determine which fields to change
            :param new_target: the new translation target (to replace the old one)
        """
        idx = np.where(self.active_df['ID'].values==entry_id)[0][0]
        entry = self.active_df.loc[idx].to_dict()
        for key, value in entry.items():
            if value == old_target:
                self.active_df.loc[self.active_df.index==idx, key] = new_target
    
    def apply_filter(self, exercise:str, n_samples:int=0, included_categories:Iterable[str]=[], excluded_categories:Iterable[str]=[]):
        """ Apply a filter to the available questions
            :param exercise: the name of the exercise to use for getting the weights when sampling
            :param n_samples: the number of samples to be set in the final filtering
            :param included_categories: the categories to be sampled in (white filter)
            :param excluded_categories: the categories to be sampled out (black filter)
        """
        df = self.active_df # Just to have a shorter code
        self.used_ids = df['ID'].values

        matches_category = lambda x, category: category in df.loc[df['ID']==x, 'Category'].values[0]
        # Exclude the categories in excluded categories
        for cat in excluded_categories:
            self.used_ids = [x for x in self.used_ids if not matches_category(x, cat)]
        # Include only the categories in included_categories
        for cat in included_categories:
            self.used_ids = [x for x in self.used_ids if matches_category(x, cat)]
        # Sample the needed number of words
        if n_samples > 0:
            sampled_entries = df.sample(n=n_samples, replace=False)
        else:
            sampled_entries = df.sample(len(df), replace=False)


        self.used_ids = sampled_entries.loc[:, 'ID'].tolist()

    def get_scores_summary(self, scores):
        """ Return the score summary for a particular exercise"""
        summary = scores.summarize()
        # Replace the ids by their names
        ids = self.active_df['ID'].values
        for key in ['max', 'min']:
            element_id = int(summary[key][0])
            idx = np.where(ids==element_id)[0][0]
            summary[key][0] = self.active_df.loc[self.active_df.index==idx, 'Word_s'].values[0]
        # Round the average score to two decimal points
        summary['average'] = round(summary['average'], 2)
        return summary

    def get_scores_path(self, exercise):
         direction = exercise.split()[-1]
         exercise_type = exercise.split()[0]
         return f'{exercise_type}_{self.active_sheet}_{direction}.json'

    def sample_random_entry(self, ids, weights) -> dict[str, str | Any] | list[
        dict[str, str | Any]]:
        """
        Sample a question for a specific exercise
        :param ids: the ids to sample from
        :param weights: the weights to assign for each id (should match ids size)
        :returns: the sampled row as a dictionary
        """
        draw = np.random.choice(ids, p=weights)

        available_ids = self.active_df['ID'].values
        indices = [np.where(available_ids==draw)[0][0]]
        entries = [self.active_df.loc[idx].to_dict() for idx in indices]
        return entries[0]

    def load_all_sheets(self, excel_file):
        # Load all sheets in the Excel file
        xlsx = pd.ExcelFile(excel_file)
        
        for sheet_name in xlsx.sheet_names:
            self.load_excel_sheet(excel_file, sheet_name)
