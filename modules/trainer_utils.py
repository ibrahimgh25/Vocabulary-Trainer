''' This package contains util functions to support the language trainer class'''

import re
from fuzzywuzzy import fuzz
from .utils import sample_entry, add_special_chars


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
