from abc import abstractmethod

class Evaluator:
    @abstractmethod
    def match_answer(self, answer, target) -> bool:
        """
        Evaluates an answer by matching it with the entry and updates the scores
        :param target: the target answer
        :param answer: the user answer
        :returns: True if the answer is right False otherwise
        """
        pass