# -*- encoding: utf-8 -*-
from uie.uie_predictor import UIEPredictor
from tools.utils import get_root_path, timer
import os

SCHEMA = ['公司名', '产品名', '技术名', '行业名', '时间', '地点']
MODEL_PATH = os.path.join(get_root_path(), 'models/uie_model_best')


class EntityExtractor:
    def __init__(self):
        # set use_fp16 to True to speed up with GPU
        self.ie = UIEPredictor(model='uie-base', task_path=MODEL_PATH, schema=SCHEMA, use_fp16=False)

    @staticmethod
    def convert_format(entities):
        _entities = []
        for item in entities:
            for key, values in item.items():
                count_dict = {}
                for value in values:
                    text = value['text']
                    count_dict[text] = count_dict.get(text, 0) + 1
                _entities.append({key: count_dict})
        return _entities

    # @timer
    def extract(self, text):
        entities = self.ie(text)
        return self.convert_format(entities)


if __name__ == '__main__':
    extractor = EntityExtractor()
    texts = '国金证券股份有限公司首次公开发行股票并在创业板上市'
    print(extractor.extract(texts))
