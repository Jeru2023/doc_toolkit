from uie.uie_predictor import UIEPredictor
from tools.utils import get_root_path, timer
import os

SCHEMA = ['公司名', '产品名', '技术名', '行业名', '时间', '地点']
MODEL_PATH = os.path.join(get_root_path(), 'models/uie_model_best')


class EntityExtractor:
    def __init__(self):
        self.ie = UIEPredictor(model='uie-base', task_path=MODEL_PATH, schema=SCHEMA)

    @timer
    def extract(self, text):
        result = self.ie(text)
        return result


if __name__ == '__main__':
    extractor = EntityExtractor()
    print(extractor.extract('柠檬茶赛道日益增长, 明年柠季如何对抗竞争!'))
