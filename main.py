import pandas as pd
import openpyxl
from typing import Iterable, Union, Optional
import re
import numpy as np
from fuzzywuzzy import fuzz


from modules.excel_ops import get_excel_df, save_to_excel

def normalize_weights(weights:Iterable) -> Iterable:
    """
    Normalizes a list of weights.
    """
    weights = - np.array(weights)
    weights[weights==0] = 1
    weights = np.where(weights < 0, 0.3 - 1/weights, weights)
    weights = weights / np.sum(weights)
    return weights

def random_sample(weights:Iterable, n:int) -> int:
    """
    Returns a random integer between 0 and n-1 from using weights.
    """
    choices = np.arange(0, n)
    weights = - weights + 1
    print(weights)
    # replace negative values with 1
    weights = np.where(weights < 0, 1, weights)
    weights = weights / np.sum(weights)
    return np.choice(choices, p=weights)

def sample_entry(entry, keys):
    keys = [x for x in keys if entry[x] != '']
    key = np.random.choice(keys)
    return entry[key], key

def add_special_chars(answer:str) -> str:
    """
    Adds special characters to the answer.
    """
    special_chars = {'s':'ß', 'a':'ä', 'o':'ö', 'u':'ü', 
                      'A':'Ä', 'O':'Ö', 'U':'Ü', 'S':'ẞ'}
    for char in special_chars.keys():
        # the special char is indicated by the english char proceeded
        # by a '_'
        answer = answer.replace(char + '_', special_chars[char])
    return answer

def guess_word(entry, direction='Forward'):
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
    if direction == 'Backward':
        query = query + ' (' + target_key.split('_')[-1] + ')'
    answer = input(query + ': ')
    answer = add_special_chars(answer)
    if matching(answer, target):
        print(target)
        return True
    elif answer == 'exit()':
        return None
    else:
        print('Wrong answer, the right answer is: ', target)
        return False

def matching(answer, target):
    correct_answers = re.sub(r"[\(\[].*?[\)\]]", "", target)
    correct_answers = re.split(',|;', correct_answers)
    for idx, correct_answer in enumerate(correct_answers):
        tmp = re.sub('\?|\.|!', '', correct_answer)
        correct_answers[idx] = tmp.lower().strip()
    answer = answer.lower()
    answer = re.sub('\?|\.|!', '', answer).strip()
    answer2 = re.sub('^the\s|^a\s', '', answer).strip()
    return any([fuzz.ratio(answer2, correct_answer) > 95 for correct_answer in correct_answers])

def delete_list_indecies(list:Iterable, indecies:Iterable[int]) -> Iterable:
    """
    Deletes a list of indecies from a list.
    """
    for index in sorted(indecies, reverse=True):
        del list[index]
    return list

if __name__=='__main__':
    excel_file = 'resources/german_database.xlsx'
    df = get_excel_df(excel_file)
    indices = list(range(len(df)))
    go_again = True
    direction = 'Backward'
    while(go_again):
        draw = np.random.choice(indices, p=normalize_weights(df[direction]))
        entry = df.iloc[draw].to_dict()
        result = guess_word(entry, direction)
        if result:
            df.loc[df.index==draw, direction] += 1
            df.loc[df.index==draw, direction] = max(0, df.iloc[draw][direction])
        elif result == False:
            df.loc[df.index==draw, direction] -= 1
        else:
            go_again = False
    
    save_to_excel(df, excel_file, 'A1 Stuff')
    print('Bye!')