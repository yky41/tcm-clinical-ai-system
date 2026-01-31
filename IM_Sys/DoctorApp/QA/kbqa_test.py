import pickle
import sklearn
from .entity_extractor import EntityExtractor
from .search_answer import AnswerSearching
# from UserApp.QA.entity_extractor import EntityExtractor
# from UserApp.QA.search_answer import AnswerSearching


class KBQA:
    def __init__(self):
        self.extractor = EntityExtractor()
        self.searcher = AnswerSearching()
        self.load_models()

    def load_models(self):
        with open(self.tfidf_path, 'rb') as f:
            self.tfidf_model = pickle.load(f)
        with open(self.nb_path, 'rb') as f:
            self.nb_model = pickle.load(f)

    def qa_main(self, input_str):
        answer = "对不起，您的问题我不知道，我今后会努力改进的哈哈哈。"
        try:
            entities = self.extractor.extractor(input_str)
        except Exception as e:
            print(e)
            entities=None
        if not entities:
            return answer
        sqls = self.searcher.question_parser(entities)
        final_answer = self.searcher.searching(sqls)
        if not final_answer:
            return answer
        else:
            return '\n'.join(final_answer)


if __name__ == "__main__":
    handler = KBQA()
    while True:
        question = input("用户：")
        if not question:
            break
        answer = handler.qa_main(question)

