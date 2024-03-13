# -*- coding:utf-8 -*-
# CREATED BY: jiangbohuai
# CREATED ON: 2021/1/21 5:23 PM
# LAST MODIFIED ON:
# AIM:
import attrdict

from .automata import condition, operation
from .automata import symbols
from .automata.white_list import data

SYMBOLS = symbols.SYMBOLS_EN


def init_nodes(**kwargs):
    max_len = kwargs.get('max_len', 25)
    min_len = kwargs.get('min_len', 5)
    # hard_max = kwargs.get('hard_max', 200)

    # --- initialize condition & operation --- #
    edges = attrdict.AttrDict({
        'is_end_symbol': condition.IsEndSymbolEN(SYMBOLS),
        'is_bracket_close': condition.IsBracketClose(SYMBOLS),
        'is_book_close': condition.IsBookClose(SYMBOLS),
        'is_quote_close': condition.IsQuoteClose(SYMBOLS),
        'is_single_quote_close': condition.IsSingleQuoteCloseEn(),
        'is_end_state': condition.IsEndState(SYMBOLS),
        'is_long_sentence': condition.IsLongSentence(SYMBOLS, max_len=max_len),
        'is_not_short_sentence': condition.IsShortSentence(SYMBOLS, min_len=min_len, reverse=True),
        'is_next_with_space': condition.IsNextWithSpace(SYMBOLS),

        # --- sepcial Condition --- #
        'special_ends': condition.SpecialEnds(),
        'not_in_white_list': condition.NotInWhitelistDotEn(data),
        'is_empty': condition.IsSpace(SYMBOLS),
        'is_left_quota': condition.IsLeftQuotaEn(),
        'is_left_single_quota': condition.IsLeftSingleQuotaEn(),
        'is_right_quota': condition.IsRightQuotaEn(),
        'is_right_single_quota': condition.IsRightSingleQuotaEn(),
        'dialogue_is_greater_than': condition.DialogueIsGreaterThanEN(length=min_len)
    })

    nodes = attrdict.AttrDict({
        'do_cut': operation.Normal(SYMBOLS, name='do_cut'),
        'cut_pre_idx': operation.CutPreIdx(SYMBOLS, name='cut_per_idx'),
        'long_handler': operation.LongHandlerEN(SYMBOLS, white_list=data, min_sentence_length=min_len,
                                                name='long_handler'),
        'init': operation.Indolent(SYMBOLS),
        'quota_handler': operation.Indolent(SYMBOLS, name='quota_handler'),
        'quota_single_handler': operation.Indolent(SYMBOLS, name='quota_single_handler'),
        #'end': operation.EndState(SYMBOLS)
    })
    nodes['end'] = operation.CleanNode(node_list=list(nodes.values()))
    return edges, nodes


def long_cuter_en(**kwargs):
    edges, nodes = init_nodes(**kwargs)
    return {
        nodes.init: [
            {'edge': edges.is_end_state,
             'node': nodes.end},

            # -- "..." "..."  -- #
            {'edge': [edges.is_right_quota,
                      edges.dialogue_is_greater_than],
             'args': all,
             'node': nodes.quota_handler},

            {'edge': [edges.is_right_single_quota,
                      edges.dialogue_is_greater_than],
             'args': all,
             'node': nodes.quota_single_handler},

            # {'edge': edges.special_ends,
            #  'node': nodes.do_cut},

            # -- normal cut -- #
            {'edge': [
                edges.is_not_short_sentence,
                edges.is_next_with_space,
                edges.is_end_symbol,
                edges.is_bracket_close,
                edges.is_quote_close,
                edges.is_single_quote_close,
                edges.not_in_white_list
            ],
                'args': all,
                'node': nodes.do_cut},

            {'edge': edges.is_long_sentence,
             'node': nodes.long_handler},

        ],

        nodes.quota_single_handler: [
            {'edge': edges.is_end_state,
             'node': nodes.end},

            {'edge': [
                edges.is_not_short_sentence,
                edges.is_left_single_quota,
            ],
                'args': all,
                'node': nodes.cut_pre_idx},

            {'edge': edges.is_empty,
             'node': nodes.quota_single_handler},

            {'edge': [
                edges.is_not_short_sentence,
                edges.is_end_symbol,
                edges.is_bracket_close,
                edges.is_book_close,
                edges.is_quote_close,
                edges.is_single_quote_close],
                'args': all,
                'node': nodes.do_cut},

            {'edge': None,
             'node': nodes.init}
        ],

        nodes.quota_handler: [
            {'edge': edges.is_end_state,
             'node': nodes.end},

            {'edge': [
                edges.is_not_short_sentence,
                edges.is_left_quota,
            ],
                'args': all,
                'node': nodes.cut_pre_idx},

            {'edge': edges.is_empty,
             'node': nodes.quota_handler},

            {'edge': [
                edges.is_not_short_sentence,
                edges.is_end_symbol,
                edges.is_bracket_close,
                edges.is_book_close,
                edges.is_quote_close,
                edges.is_single_quote_close],
                'args': all,
                'node': nodes.do_cut},  # do_cut},

            {'edge': None,
             'node': nodes.init}
        ],

        nodes.cut_pre_idx: [
            {'edge': edges.is_end_state,
             'node': nodes.end},

            {'edge': None,  # else 状态
             'node': nodes.init},
        ],

        nodes.do_cut: [
            {'edge': edges.is_end_state,
             'node': nodes.end},

            {'edge': None,  # else 状态
             'node': nodes.init},
        ],
        nodes.long_handler: [
            {'edge': edges.is_end_state,
             'node': nodes.end},

            {'edge': None,  # else 状态
             'node': nodes.init},
        ]
    }
