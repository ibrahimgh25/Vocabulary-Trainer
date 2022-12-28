import re

from fuzzywuzzy import fuzz
from typing import Tuple, List, Union

from ..utils.utils import add_special_chars, clean_text


class FuzzyEvaluator:
    def match_answer(self, answer, target) -> bool:
        # Handle for special characters that you're too lazy to type (like: Ö)
        answer = add_special_chars(answer)

        result = self.matching(answer, target)
        return result

    def matching(self, answer:str, target:str) -> bool:
        """
        Sees whether the answer matches the target or not
        :param answer: the answer provided by the user
        :param target: the correct answer
        :returns: True if the answer is matching else False
        """
        target_parts = re.split('[,;]', clean_text(target))
        correct_answers = []
        for value in [self.get_all_valid_answers(x) for x in target_parts]:
            correct_answers += [x.strip() for x in value if x.strip() not in correct_answers]

        answer = clean_text(answer)
        # we'll use the fuzzywuzzy library to have some flexibility, but not too much
        return any([fuzz.ratio(answer, correct_answer) > 90 for correct_answer in correct_answers])

    def get_all_valid_answers(self, sentences:Union[str, List[str]], choices:List[Tuple[str, List[str]]]=[]):
        """
        Decomposes an answer to all possible implied answers
        :param sentences: a list of valid answers
        :param choices:  the tuple the function got so far, it contains the
         word and the possible replacements used by the function to guide recursion
        :returns: a list of strings containing the valid answers
        """
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
        return self.get_all_valid_answers(sentences, choices)