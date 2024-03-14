# -*- coding:utf-8 -*-
# CREATED BY: bohuai jiang 
# CREATED ON: 2020/8/7 3:50 PM
# LAST MODIFIED ON: 2021/3/1 3:46 PM
# AIM:
from abc import ABC
from typing import List, Union
import re

from .abc import Criteria
from .sequence import StrSequence, EnSequence
from .symbols import SYMBOLS, SYMBOLS_EN
from .white_list import data
import copy


class IsEndState(Criteria):
    def __init__(self, symbols: dict):
        super(IsEndState, self).__init__('IsEndState', symbols)

    def accept(self, state: StrSequence) -> bool:
        return state.reach_right_end()


class IsEndSymbolZH(Criteria):
    def __init__(self, symbols: dict, white_list: str = data):
        super(IsEndSymbolZH, self).__init__('IsEndSymbolEN', symbols)
        self.empty = re.compile('^\s+$')
        self.number = re.compile('[0-9]')
        self.is_right_quota = IsRightQuotaEn()
        self.is_right_s_quota = IsRightSingleQuotaEn()
        self.is_bracket_close = IsBracketClose(symbols)
        self.is_quote_close = IsQuoteClose(symbols)
        self.is_book_close = IsBookClose(symbols)

    def look_forward(self, state: StrSequence) -> str:
        for i in range(state.v_pointer + 1, state.length):
            if not self.empty.match(state[i]):
                return state[i]
        else:
            return state.current_value

    def look_forward_state(self, state: StrSequence) -> StrSequence:
        state_copy = copy.copy(state)
        for i in range(state_copy.v_pointer + 1, state_copy.length):
            # print(f"{state.current_value} -> {state_copy[i]}")
            if not self.empty.match(state_copy[i]):
                state_copy.add_to_candidate()
                return state_copy
            state_copy.add_to_candidate()
        else:
            return state_copy

    def is_right_clone(self, state: StrSequence) -> bool:
        state = self.look_forward_state(state)
        if self.symbols['bracket_right'].match(state.current_value) and self.is_bracket_close.accept(state):
            return True
        if self.symbols['quotation_right'].match(state.current_value) and self.is_quote_close.accept(state):
            return True
        if self.symbols['book_right'].match(state.current_value) and self.is_book_close.accept(state):
            return True
        return False

    def look_backward(self, state: StrSequence) -> str:
        for i in range(0, state.v_pointer)[::-1]:
            if not self.empty.match(state[i]):
                return state[i]
        else:
            return state.current_value

    def accept(self, state: StrSequence) -> bool:
        if self.symbols['en_dot'].match(state.current_value):
            if self.number.match(state.next_value):
                return False
            else:
                return True
        if self.symbols['end_symbols'].match(state.current_value):
            if not self.is_right_clone(self.look_forward_state(state)):
                return True
            if not self.symbols['all_symbols'].match(self.look_forward(state)):
                return True
        if (self.is_right_quota(state) or self.is_right_s_quota(state)) and self.symbols['end_symbols'].match(
                self.look_backward(state)):
            return True

        return False


class IsEndSymbolEN(Criteria):
    def __init__(self, symbols: dict, white_list: str = data):
        super(IsEndSymbolEN, self).__init__('IsEndSymbolEN', symbols)
        self.empty = re.compile('^\s+$')
        self.number = re.compile('[0-9]')
        self.is_right_quota = IsRightQuotaEn()
        self.is_right_s_quota = IsRightSingleQuotaEn()
        self.not_in_white_list = NotInWhitelistDotEn(white_list=white_list)

    def look_forward(self, state: EnSequence, by_idx: bool = False) -> Union[str, int]:
        for i in range(state.v_pointer + 1, state.length):
            if not self.empty.match(state[i]):
                if by_idx:
                    return i
                else:
                    return state[i]
        else:
            if by_idx:
                return state.v_pointer
            else:
                return state.current_value

    def look_backward(self, state: EnSequence, by_idx: bool = False) -> Union[str, int]:
        for i in range(0, state.v_pointer)[::-1]:
            if not self.empty.match(state[i]):
                if by_idx:
                    return i
                else:
                    return state[i]
        else:
            if by_idx:
                return state.v_pointer
            else:
                return state.current_value

    def accept(self, state: EnSequence) -> bool:
        if self.is_right_quota(state):
            print()

        if self.symbols['end_symbols'].match(state.current_value) and not self.symbols['end_symbols'].match(
                self.look_forward(state)):
            return True
        if (self.is_right_quota(state) or self.is_right_s_quota(state)) and self.symbols['end_symbols'].match(
                self.look_backward(state)) and self.look_forward(state)[
            0].isupper() and self.not_in_white_list.is_valid(state, self.look_backward(state, by_idx=True)):
            return True
        return False


class IsComma(Criteria):
    def __init__(self, symbols: dict):
        super(IsComma, self).__init__('IsComma', symbols)

    def accept(self, state: StrSequence) -> bool:
        if self.symbols['comma'].match(state.current_value):
            return True
        return False


class IsBracketClose(Criteria):
    def __init__(self, symbols: dict):
        super(IsBracketClose, self).__init__('IsBracketClose', symbols)

    def accept(self, state: StrSequence) -> bool:
        # -- avoid endless loop -- #
        if state.reach_right_end():
            return True
        if state.bracket_left <= state.bracket_right:
            state.reset_bracket()
            return True
        else:
            return False


class IsQuoteClose(Criteria):
    def __init__(self, symbols: dict):
        super(IsQuoteClose, self).__init__('IsQuoteClose', symbols)

    def accept(self, state: StrSequence) -> bool:
        # -- avoid endless loop -- #
        if state.reach_right_end():
            return True

        if state.quota_en > 0:
            if (state.quota_en + state.quota_left) % 2 == 0:
                state.reset_quota()
                return True
            else:
                return False
        elif state.quota_left > 0:
            return False
        else:
            return True


class IsSingleQuoteCloseEn(Criteria):
    def __init__(self):
        super(IsSingleQuoteCloseEn, self).__init__('IsSingleQuoteCloseEn', SYMBOLS_EN)

    def accept(self, state: EnSequence) -> bool:
        # -- avoid endless loop -- #
        if state.reach_right_end():
            return True

        if state.s_quota_en > 0:
            if (state.s_quota_en + state.s_quota_left) % 2 == 0:
                state.reset_s_quota()
                return True
            else:
                return False
        elif state.s_quota_left > 0:
            return False
        else:
            return True


class IsBookClose(Criteria):
    def __init__(self, symbols: dict):
        super(IsBookClose, self).__init__('IsBookClose', symbols)

    def accept(self, state: StrSequence) -> bool:
        # -- avoid endless loop -- #
        if state.reach_right_end():
            return True
        if state.book_left <= state.book_right:
            # state.reset_bookmark()
            return True
        else:
            return False


class IsLongSentence(Criteria):
    def __init__(self, symbols: dict, max_len: int = 128):
        super(IsLongSentence, self).__init__('IsLongSentence', symbols)
        self.max_len = max_len

    def accept(self, state: StrSequence) -> bool:
        if state.candidate_len > self.max_len:
            return True
        return False


class IsShortSentence(Criteria):
    def __init__(self, symbols: dict, min_len: int = 17, **kwargs):
        super(IsShortSentence, self).__init__('IsShortSentence', symbols, **kwargs)
        self.min_len = min_len

    def accept(self, state: StrSequence) -> bool:
        if state.candidate_len < self.min_len:
            return True
        return False


class IsSQuota(Criteria):
    def __init__(self, value: str):
        super(IsSQuota, self).__init__('Criteria', SYMBOLS_EN)
        self.value = value
        assert self.value in ['en', 'left', 'right']
        if self.value == 'left':
            self.pattern = self.symbols['s_quota_left']
        elif self.value == 'right':
            self.pattern = self.symbols['s_quota_right']
        else:
            self.pattern = self.symbols['s_quota_en']
        self.is_blank = re.compile('^\s+')

    def accept(self, state: StrSequence) -> bool:
        if self.pattern.match(state.current_value):
            if state.v_pointer == 0:
                return True
            elif state.v_pointer == state.length - 1:
                return True
            elif self.is_blank.match(state.pre_value) or self.is_blank.match(state.next_value):
                return True
            else:
                return False
        return False


# --- space --- #

class IsSpace(Criteria):
    def __init__(self, symbols: dict):
        super(IsSpace, self).__init__('IsSpace', symbols)
        self.pattern = re.compile('\s')

    def accept(self, state: StrSequence) -> bool:
        if self.pattern.match(state.current_value):
            return True
        else:
            return False


class IsNestSpace(Criteria):
    def __init__(self, symbols: dict):
        super(IsNestSpace, self).__init__('IsNestSpace', symbols)
        self.pattern = re.compile('\s')

    def accept(self, state: StrSequence) -> bool:
        if self.pattern.match(state.next_value):
            return True
        else:
            return False


class IsNextWithSpace(Criteria):
    def __init__(self, symbols: dict):
        super(IsNextWithSpace, self).__init__('IsNextWithSpace', symbols)
        self.pattern = re.compile('\s')

    def accept(self, state: StrSequence) -> bool:
        if self.pattern.match(state.next_value):
            return True
        return False


class IsNextWithEndQuota(Criteria):
    def __init__(self, symbols: dict):
        super(IsNextWithEndQuota, self).__init__('IsNextWithQuota', symbols)

    def accept(self, state: StrSequence) -> bool:
        if self.symbols['quotation_right'].match(state.next_value):
            return True
        elif self.symbols['quotation_en'].match(state.next_value):  # and (state.quota_en + state.quota_left)%2 != 0
            return True
        return False


# =========================== #
#      Special Condition      #
# =========================== #

class SpecialCondition(Criteria, ABC):
    pass


class IsRightQuotaZH(SpecialCondition):
    def __init__(self, index=0):
        super(IsRightQuotaZH, self).__init__('IsRightQuota', SYMBOLS)
        self.index = index

    def accept(self, state: StrSequence) -> bool:
        if self.index >= 0:
            index = min(state.v_pointer + self.index, state.length - 1)
        else:
            index = max(0, state.v_pointer + self.index)
        if self.symbols["quotation_right"].match(state[index]):
            state.reset_quota()
            return True
        return False


class IsLeftQuotaZH(SpecialCondition):
    def __init__(self, index=0):
        super(IsLeftQuotaZH, self).__init__('IsLeftQuotaZH', SYMBOLS)
        self.index = index

    def accept(self, state: StrSequence) -> bool:
        if self.index >= 0:
            index = min(state.v_pointer + self.index, state.length - 1)
        else:
            index = max(0, state.v_pointer + self.index)
        if SYMBOLS["quotation_left"].match(state[index]):
            return True
        return False


class IsLeftQuotaEn(SpecialCondition):
    def __init__(self):
        super(IsLeftQuotaEn, self).__init__('IsListQuota', SYMBOLS_EN)
        self.blank = re.compile('\s')

    def accept(self, state: StrSequence) -> bool:
        if self.symbols['quotation_en'].match(state.current_value) and state.quota_en % 2 != 0 or self.symbols[
            'quotation_left'].match(state.current_value):
            # state.v_pointer = max(0, state.v_pointer - 1)
            return True

        # if self.symbols['quotation_en'].match(state.current_value) and (not self.blank.match(state.next_value)) or \
        #         self.symbols[
        #             'quotation_left'].match(state.current_value):
        #     # state.v_pointer = max(0, state.v_pointer - 1)
        #     return True
        return False


class IsLeftSingleQuotaEn(SpecialCondition):
    def __init__(self):
        super(IsLeftSingleQuotaEn, self).__init__('IsLeftSingleQuotaEn', SYMBOLS_EN)
        self.blank = re.compile('\s')

    def accept(self, state: EnSequence) -> bool:
        if self.symbols['s_quota_en'].match(state.current_value) and state.s_quota_en % 2 != 0 or self.symbols[
            's_quota_left'].match(state.current_value):
            # state.v_pointer = max(0, state.v_pointer - 1)
            return True

        return False


class IsRightQuotaEn(SpecialCondition):
    def __init__(self):
        super(IsRightQuotaEn, self).__init__('SpecialCondition', SYMBOLS_EN)
        self.blank = re.compile('\s')

    def accept(self, state: StrSequence) -> bool:
        if self.symbols['quotation_en'].match(state.current_value) and state.quota_en % 2 == 0 or self.symbols[
            'quotation_right'].match(state.current_value):
            return True

        # if self.symbols['quotation_en'].match(state.current_value) and (
        #         not self.blank.match(state.pre_value)) and state.v_pointer > 0 or \
        #         self.symbols['quotation_right'].match(state.current_value):
        #     # state.v_pointer = max(0, state.v_pointer - 1)
        #     return True
        return False


class IsRightSingleQuotaEn(SpecialCondition):
    def __init__(self):
        super(IsRightSingleQuotaEn, self).__init__('IsRightSingleQuotaEn', SYMBOLS_EN)
        self.blank = re.compile('\s')

    def accept(self, state: EnSequence) -> bool:
        if self.symbols['s_quota_en'].match(state.current_value) and state.s_quota_en % 2 == 0 or self.symbols['s_quota_right'].match(state.current_value):
            return True

        return False


class DialogueIsGreaterThanEN(SpecialCondition, ABC):
    def __init__(self, length: int):
        super(DialogueIsGreaterThanEN, self).__init__('DialogueIsGreaterThanEN', SYMBOLS_EN)
        self.length = length
        self.word_pattern = re.compile('^[a-zA-Z0-9]+')

    def accept(self, state: EnSequence) -> bool:
        if state.v_pointer < self.length:
            return False
        i = state.v_pointer
        n_quota = 0
        n_s_quota = 0
        n_word = 0
        s_quota_result = True
        quota_result = True
        while i >= 0:
            if self.symbols['all_quota'].match(state[i]):
                n_quota += 1
            if self.symbols['all_s_quota'].match(state[i]):
                n_s_quota += 1
            if n_quota >= 2:
                quota_result = False
            if n_s_quota >= 2:
                s_quota_result = False
            if self.word_pattern.match(state[i]):
                n_word += 1
                if n_word >= self.length:
                    break
            i -= 1
        if n_quota == 0 and n_s_quota != 0:
            return s_quota_result
        elif n_quota != 0 and n_s_quota == 0:
            return quota_result
        else:
            return s_quota_result or quota_result


class BracketIsGreaterThan(SpecialCondition):
    def __init__(self, length: int, symbols: dict):
        super(BracketIsGreaterThan, self).__init__('BracketIsGreaterThan', symbols)
        self.length = length
        self.word_pattern = re.compile('^[a-zA-Z0-9]+')

    def accept(self, state: StrSequence) -> bool:
        if state.v_pointer < self.length:
            return False
        i = state.v_pointer
        out = True
        n_word = 0
        while i >= 0:
            if self.symbols["bracket_left"].match(state[i]):
                out = False
            if self.word_pattern.match(state[i]):
                n_word += 1
                if n_word > self.length:
                    break
            i -= 1
        return out


class IsLeftQuotaGreaterThan(SpecialCondition):
    '''
    左引号 重复次数大于一定值
    '''

    def __init__(self, theta: int = 1):
        super(IsLeftQuotaGreaterThan, self).__init__('IsLeftQuotaGreaterThan', SYMBOLS)
        self.theta = theta

    def accept(self, state: StrSequence) -> bool:
        if state.quota_left > self.theta:
            state.reset_quota()
            state.v_pointer -= 1
            return True


class IsRQuotaStickWithLQuota(SpecialCondition):
    '''
    右引号紧跟着左引号
    '''

    def __init__(self):
        super(IsRQuotaStickWithLQuota, self).__init__('IsRQuotaStickWithLQuota', SYMBOLS)

    def accept(self, state: StrSequence) -> bool:
        if self.symbols['quotation_right'].match(state.current_value) and \
                self.symbols['quotation_left'].match(state.next_value):
            return True
        return False


class WithSays(SpecialCondition):
    def __init__(self):
        super(WithSays, self).__init__('WithSays', SYMBOLS)
        self.pattern = re.compile('([他她](说|说道|笑道|道))+')

    def accept(self, state: StrSequence) -> bool:
        sentence = state[state.v_pointer + 1:15]
        if self.pattern.match(sentence):
            return True
        return False


class SpecialEnds(SpecialCondition):
    def __init__(self):
        super(SpecialEnds, self).__init__('SpecialEnds', SYMBOLS)
        self.pattern_pre = re.compile('([~～])')
        self.pattern_cur = re.compile('\s')

    def accept(self, state: StrSequence) -> bool:
        if self.pattern_pre.match(state.pre_value) and self.pattern_cur.match(state.current_value):
            return True
        else:
            return False


class NotInWhitelistDotEn(SpecialCondition):
    '''
    note: 大小写敏感
    '''

    def __init__(self, white_list: str):
        super(NotInWhitelistDotEn, self).__init__('NotInWhitelistDotEn', SYMBOLS_EN)
        self.white_list = [v.strip() for v in white_list.splitlines()]

    def accept(self, state: EnSequence) -> bool:
        return self.is_valid(state, state.v_pointer)
        # if not state.current_value in ['.', '!']:
        #     return True
        # else:
        #     for word in self.white_list:
        #         if not word:
        #             continue
        #         word_token = state.tokenize(word)
        #         dots_pos = self.find_dot(word_token)
        #         word_len = len(word_token)
        #         atcual_word = ''.join(state[state.v_pointer - dots_pos:state.v_pointer])
        #         if dots_pos == word_len and word == atcual_word:
        #             return False
        #         if dots_pos != word_len:
        #             # case Mac. book 走搜索
        #             while dots_pos > 0:
        #                 i = 0
        #                 whole_word = atcual_word + ''.join(
        #                     state[state.v_pointer:state.v_pointer + i + word_len - dots_pos])
        #                 if word == whole_word:
        #                     # state.v_pointer = state.v_pointer + i + word_len - dots_pos
        #                     return False
        #                 dots_pos = self.find_dot(word_token, dots_pos + 1)
        #                 atcual_word = ''.join(state[state.v_pointer - dots_pos:state.v_pointer])
        #     return True

    def is_valid(self, state: EnSequence, index: int):
        if not state[index] in ['.', '!']:
            return True
        else:
            for word in self.white_list:
                if not word:
                    continue
                word_token = state.tokenize(word)
                dots_pos = self.find_dot(word_token)
                word_len = len(word_token)
                atcual_word = ''.join(state[index - dots_pos:index + 1])
                if dots_pos == word_len - 1 and word == atcual_word:
                    return False
                if dots_pos != word_len - 1:
                    # case Mac. book 走搜索
                    while dots_pos > 0:
                        whole_word = atcual_word + ''.join(
                            state[index + 1:index + word_len - dots_pos])
                        if word == whole_word:
                            # state.v_pointer = state.v_pointer + i + word_len - dots_pos
                            return False
                        dots_pos = self.find_dot(word_token, dots_pos + 1)
                        atcual_word = ''.join(state[index - dots_pos:index+1])
            return True

    def find_dot(self, str_list: List[str], start=0):
        for i, v in enumerate(str_list[start::]):
            if v in ['.', '!']:
                return i + start
        return -1


class IsSenetnecDash(SpecialCondition):
    '''
    检查是否是引文短句dash
    '''

    def __init__(self):
        super(IsSenetnecDash, self).__init__('IsSenetnecDash', SYMBOLS_EN)

    def accept(self, state: StrSequence) -> bool:
        if self.symbols['dash'].match(state.current_value):
            return True
        if self.symbols['short_dash'].match(state.current_value) and self.symbols['short_dash'].match(state.pre_value):
            return True
        return False
