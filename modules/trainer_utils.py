''' This package contains util functions to support the language trainer class'''

import re
from fuzzywuzzy import fuzz
from .utils import sample_entry, add_special_chars

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
    # we'll use the fuzzywuzzy library to have some flexibility, but not too much
    return any([fuzz.ratio(answer2, correct_answer) > 95 for correct_answer in correct_answers])
