#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import logging
import torch

from bert.tokenization import BertTokenizer
from tools import utils
from coreference import Coreference

CONFIG_CATEGORY = "bert_base_chinese"


class CorefModel:
    def __init__(self):
        self.device = utils.get_device()
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(41)
        else:
            torch.manual_seed(41)

    @staticmethod
    def load_config():
        config = utils.read_config(CONFIG_CATEGORY, "config.conf")
        return config

    @staticmethod
    def format(text, tokenizer):
        """将文字转为模型需要的样例格式"""
        sentences = [['[CLS]'] + tokenizer.tokenize_not_UNK(text) + ['[SEP]']]
        sentence_map = [0] * len(sentences[0])
        speakers = [["-" for _ in sentence] for sentence in sentences]
        subtoken_map = [i for i in range(len(sentences[0]))]
        return {
            "doc_key": "bn",
            "clusters": [],
            "sentences": sentences,
            "speakers": speakers,
            'sentence_map': sentence_map,
            'subtoken_map': subtoken_map
        }

    def predict(self, input_text):
        """
        输入一段文本，进行指代消解任务
        :param input_text: 文本
        :return: None
        """
        config = self.load_config()

        vocab_file = utils.get_root_path() + '/models/' + config['vocab_file']
        tokenizer = BertTokenizer.from_pretrained(vocab_file, do_lower_case=True)

        coref_dict = self.format(input_text, tokenizer)
        model_save_path = utils.get_root_path() + '/models/' + config["model_save_path"]
        model = Coreference.from_pretrained(model_save_path, coref_task_config=config)

        device = self.device
        model.to(device)
        model.eval()

        try:
            with torch.no_grad():
                tensorized_example = model.tensorize_example(coref_dict, is_training=False)

                input_ids = torch.from_numpy(tensorized_example[0]).long().to(device)
                input_mask = torch.from_numpy(tensorized_example[1]).long().to(device)
                text_len = torch.from_numpy(tensorized_example[2]).long().to(device)
                speaker_ids = torch.from_numpy(tensorized_example[3]).long().to(device)
                genre = torch.tensor(tensorized_example[4]).long().to(device)
                is_training = tensorized_example[5]
                gold_starts = torch.from_numpy(tensorized_example[6]).long().to(device)
                gold_ends = torch.from_numpy(tensorized_example[7]).long().to(device)
                cluster_ids = torch.from_numpy(tensorized_example[8]).long().to(device)
                sentence_map = torch.Tensor(tensorized_example[9]).long().to(device)

                (_, _, _, top_span_starts, top_span_ends, top_antecedents, top_antecedent_scores), _ = \
                    model(input_ids, input_mask, text_len, speaker_ids, genre,
                          is_training, gold_starts, gold_ends,
                          cluster_ids, sentence_map)

                predicted_antecedents = model.get_predicted_antecedents(top_antecedents,
                                                                        top_antecedent_scores)
                # 预测实体索引
                coref_dict["predicted_clusters"], _ = model.get_predicted_clusters(top_span_starts, top_span_ends,
                                                                                   predicted_antecedents)
                # 索引——>文字
                sentence = utils.flatten(coref_dict["sentences"])
                predicted_list = []
                for same_entity in coref_dict["predicted_clusters"]:
                    same_entity_list = []
                    num_same_entity = len(same_entity)
                    for index in range(num_same_entity):
                        entity_name = ''.join(sentence[same_entity[index][0]: same_entity[index][1] + 1])
                        same_entity_list.append(entity_name)
                    predicted_list.append(same_entity_list)
                    same_entity_list = []  # 清空list

                coref_dict["predicted_idx2entity"] = predicted_list
                coref_dict["top_spans"] = list(zip((int(i) for i in top_span_starts), (int(i) for i in top_span_ends)))
                coref_dict['head_scores'] = []
            return coref_dict
        except KeyError as e:
            print("Key Error: ", e)

    @staticmethod
    def show_verbose(coref_dict):
        print('======output======')
        clusters = coref_dict["predicted_clusters"]
        predicted_list = coref_dict["predicted_idx2entity"]
        if len(clusters) == 0:
            print("*** Empty Result***")
        else:
            print('predicted_idx2entity:', predicted_list)
            print('predicted_clusters:', clusters)
            print('------context------')

            for i in range(len(clusters)):
                print(f'*** group {i} ***')
                cluster = clusters[i]
                print('entity:', cluster)
                for j in range(len(cluster)):
                    item = cluster[j]
                    start_index = item[0]
                    end_index = item[1]
                    if (end_index + 5) <= len(coref_dict["sentences"][0]):
                        end_index += 5
                    print('context:', coref_dict["sentences"][0][start_index:end_index + 1])


if __name__ == "__main__":
    content = """
    柠檬茶品类在广东起源，最早是香港的冻柠茶？，-后来发展成了广式柠檬茶。因此，柠季进军广东时非常谨慎。就像海底捞进军四川一样。我们也要考虑品牌势力，没起来之前不敢轻易进入广东。我们先要建立自己的团队能力，然后再将品牌势力扩展到这个市场中。因此，在2023年1月14日进广开店的过程中我们做了一系列的准备工作。首先是网络规划。我们首先需要设定区域和预测经营情况。我们会收集全国的数据，看看哪些区域适合开店，哪些区域人口密度较高，然后根据选址系统进行经营预测。选址系统对我们来说非常重要，因为它需要考虑很多维度。选址系统做好后，我们评估这个地区的门店是否能够达到预期内营收，回算看租金是否占到营收的15%以内。如果超过15%，我们通常不会让加盟商开店，或者选择更强实力或更职业的加盟商来管理。我们在做加盟的时候，一直在讲，加盟商不是复制我的商业模式，而是复制我的盈利模式。在这个城市能赚钱，在下个城市还能够赚钱，在这个国家能够赚钱，在下个国家还能够赚钱。这个才是你最牛的地方。
    """

    coref_model = CorefModel()
    coref_dict = coref_model.predict(content)
    print(content)
    print(coref_model.show_verbose(coref_dict))
