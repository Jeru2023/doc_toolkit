# -*- coding:utf-8 -*-
# CREATED BY: bohuai jiang 
# CREATED ON: 2020/8/16 5:34 PM
# LAST MODIFIED ON: 2020/10/27 6:07 PM
# AIM:
import sys
from typing import Union, List
import re

from .symbols import SYMBOLS, SYMBOLS_EN


def print_percent(current: int, max: int, header: str = ''):
    percent = float(current) / max * 100
    sys.stdout.write("\r{0}{1:.3g}%".format(header, percent))


class StrSequence:
    def __init__(self, str_block: str, verbose=None, symbols=SYMBOLS):
        self.value = str_block
        # -- pointers -- #
        self.v_pointer = -1
        self.sentence_start = 0
        # -- results -- #
        self.sentence_list_idx = []
        self.length = len(self.value)
        self.verbose = verbose
        if verbose is None and len(self.value) > 50000:
            self.verbose = True

        # -- other pointers -- #
        self.bracket_left = 0
        self.bracket_right = 0
        self.quota_left = 0
        self.quota_en = 0
        self.book_left = 0
        self.book_right = 0
        self.symbols = symbols

        self.__candidate_len = 0
        self.s_quota_en = 0
        self.s_quota_left = 0
        self.is_blank = re.compile('^\s+')

    # -- magic method -- #
    def __str__(self):
        return self.value[self.sentence_start:self.v_pointer]

    def __getitem__(self, item: int):
        return self.value[item]

    @property
    def pre_value(self):
        return self[max(0, self.v_pointer - 1)]

    @property
    def next_value(self):
        return self[min(self.length - 1, self.v_pointer + 1)]

    @property
    def candidate_len(self):
        return self.v_pointer - self.sentence_start + 1

    @property
    def current_value(self):
        if self.value:
            return self.value[self.v_pointer]
        else:
            return ''

    def sentence_list(self):
        out = []
        for v in self.sentence_list_idx:
            if v[0] < v[1]:
                if isinstance(self.value, str):
                    out.append(self.value[v[0]:v[1]])
                else:
                    sentence = ''.join(self.value[v[0]:v[1]])
                    if sentence:
                        out.append(sentence)
        return out

    def at_end_pos(self):
        return self.v_pointer >= self.length

    def add_to_candidate(self):
        self.v_pointer = min(self.v_pointer + 1, self.length)
        # -- update pointer -- #
        self.update_barcket()
        self.update_quota()
        self.update_bookmark()
        if self.verbose:
            print_percent(self.v_pointer, self.length, 'process cutting ')

    def add_to_sentence_list(self):
        self.sentence_list_idx.append((self.sentence_start, min(self.length, self.v_pointer + 1)))
        self.sentence_start = self.v_pointer + 1

    def reach_right_end(self):
        if self.v_pointer >= self.length - 1:
            self.v_pointer = self.length - 1
            return True
        else:
            return False

    # --- update pointer --- #
    def update_barcket(self):
        key = self.current_value
        if self.symbols['bracket_left'].match(key):
            self.bracket_left += 1
        if self.symbols['bracket_right'].match(key):
            self.bracket_right += 1

    def reset_bracket(self):
        self.bracket_left = 0
        self.bracket_right = 0

    def update_quota(self):
        word = self.current_value
        if self.symbols['quotation_en'].match(word):
            self.quota_en += 1
        if self.symbols['quotation_left'].match(word):
            self.quota_left += 1
        if self.symbols['quotation_right'].match(word):
            self.quota_en = 0
            self.quota_left = 0

    def reset_quota(self):
        self.quota_en = 0
        self.quota_left = 0

    def update_bookmark(self):
        word = self.current_value
        if self.symbols['book_left'].match(word):
            self.book_left += 1
        if self.symbols['book_right'].match(word):
            self.book_right += 1

    def reset_bookmark(self):
        self.book_left = 0
        self.book_right = 0


class EnSequence(StrSequence):
    def __init__(self, str_block: str, verbose=None, symbols=SYMBOLS_EN):
        super().__init__(str_block, verbose, symbols)
        self.value = self.tokenize(str_block)
        self.length = len(self.value)
        self.__candidate_len = 0
        self.s_quota_en = 0
        self.s_quota_left = 0
        self.is_blank = re.compile('^\s+')

    def tokenize(self, str_block: str):
        pattern: re.Pattern = self.symbols['all_symbols']
        return [v for v in pattern.split(str_block) if v]

    def __is_squota(self, re):
        if re.match(self.current_value):
            if self.v_pointer == 0:
                return True
            elif self.v_pointer == self.length - 1:
                return True
            elif self.is_blank.match(self.pre_value) or self.is_blank.match(self.next_value):
                if self.pre_value not in ['s','n']:
                    return True
            else:
                return False
        return False

    def update_quota(self):
        word = self.current_value
        if self.symbols['quotation_en'].match(word):
            self.quota_en += 1
        if self.symbols['quotation_left'].match(word):
            self.quota_left += 1
        if self.symbols['quotation_right'].match(word):
            self.quota_en = 0
            self.quota_left = 0
        # -- single quota -- #
        if self.__is_squota(self.symbols['s_quota_left']):
            self.s_quota_left += 1
        if self.__is_squota(self.symbols['s_quota_en']):
            self.s_quota_en += 1
        if self.__is_squota(self.symbols['quotation_right']):
            self.s_quota_left = 0
            self.s_quota_en = 0

    def reset_s_quota(self):
        self.s_quota_en = 0
        self.s_quota_left = 0

    @property
    def candidate_len(self):
        return self.__candidate_len

    def add_to_candidate(self):
        self.v_pointer = min(self.v_pointer + 1, self.length - 1)
        if not self.symbols['all_symbols'].match(self.current_value):
            self.__candidate_len += 1

        # -- update pointer -- #
        self.update_barcket()
        self.update_quota()
        self.update_bookmark()
        if self.verbose:
            print_percent(self.v_pointer, self.length, 'process cutting')

    def add_to_sentence_list(self):
        self.sentence_list_idx.append((self.sentence_start, min(self.length, self.v_pointer + 1)))
        self.sentence_start = self.v_pointer + 1
        self.__candidate_len = 0
