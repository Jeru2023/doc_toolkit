#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import logging
import torch

from bert.tokenization import BertTokenizer
from tools import utils
from coreference import CorefModel

# from utils import get_root_path

format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
logging.basicConfig(format=format)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def create_example(text, tokenizer):
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


def predict(config, input_text):
    """
    输入一段文本，进行指代消解任务
    :param config: 配置参数
    :return: None
    """
    vocab_file = utils.get_root_path() + '/models/' + config['vocab_file']
    tokenizer = BertTokenizer.from_pretrained(vocab_file, do_lower_case=True)

    coref_dict = create_example(input_text, tokenizer)
    model_save_path = utils.get_root_path() + '/models/' + config["model_save_path"]
    model = CorefModel.from_pretrained(model_save_path, coref_task_config=config)
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

            predicted_antecedents = model.get_predicted_antecedents(top_antecedents.cpu(),
                                                                    top_antecedent_scores.cpu())
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

    os.environ["data_dir"] = "./data"
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = "2"

    config_category = "bert_base_chinese"
    config = utils.read_config(config_category, "config.conf")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(41)
    else:
        torch.manual_seed(41)

    test_file = 'sample_data_300_new.txt'
    with open(test_file, "r") as f:
        text = f.read().replace("\n", "").replace('”', '')

    coref_dict = predict(config, text)
    print(text)
    print(show_verbose(coref_dict))
