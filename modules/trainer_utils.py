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
    if direction == 'Backward' and target_key != '':
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
    def clean_text(text):
        text = re.sub(r"[\(\[].*?[\)\]]", "", text)
        text = text.replace('’', '\'')
        return re.sub('\?|\.|!', '', text).strip().lower()
    
    correct_answers = re.split(',|;', clean_text(target))
    for value in [adjust_for_slash(x) for x in correct_answers]:
        correct_answers += value

    answer = re.sub('^the\s|^a\s', '', clean_text(answer)).strip()
    # we'll use the fuzzywuzzy library to have some flexibility, but not too much
    return any([fuzz.ratio(answer, correct_answer.strip()) > 95 for correct_answer in correct_answers])

def adjust_for_slash(sentences:str, choices=[]):
    if isinstance(sentences, str):
        sentences = [sentences]
        words_with_slash = re.findall(r'[^ ]+/[^ ]+', sentences[0])    
        choices = [(x, x.split('/')) for x in words_with_slash]
    if len(choices) == 0:
        return sentences
    choice = choices[0]
    choices.remove(choice)
    tmp = sentences
    sentences = []
    for sent in tmp:
        sentences += [sent.replace(choice[0], x, 1) for x in choice[1]]
    return adjust_for_slash(sentences, choices)
