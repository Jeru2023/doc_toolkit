# -*- coding:utf-8 -*-
# CREATED BY: bohuai jiang 
# CREATED ON: 2020/8/14 4:35 PM
# LAST MODIFIED ON: 2020/10/27 7:04 PM
# AIM:
import attrdict

from .automata import condition, operation
from .automata import symbols

SYMBOLS = symbols.SYMBOLS


def init_nodes(**kwargs):
    max_len = kwargs.get('max_len', 128)
    hard_max = kwargs.get('hard_max', 300)
    min_len = kwargs.get('min_len', 15)

    # --- initialize condition & operation --- #
    edges = attrdict.AttrDict({
        'is_end_symbol': condition.IsEndSymbolZH(SYMBOLS),
        'is_bracket_close': condition.IsBracketClose(SYMBOLS),
        'is_book_close': condition.IsBookClose(SYMBOLS),
        'is_quote_close': condition.IsQuoteClose(SYMBOLS),
        'is_end_state': condition.IsEndState(SYMBOLS),
        'is_long_sentence': condition.IsLongSentence(SYMBOLS, max_len=max_len),
        'is_short_sentence': condition.IsShortSentence(SYMBOLS, min_len=min_len),
        # --- sepcial Condition --- #
        'is_right_quota': condition.IsRightQuotaZH(),
        'is_left_quota': condition.IsLeftQuotaZH(index=1),
        'is_leftQ_gt_1': condition.IsLeftQuotaGreaterThan(theta=1),
        'is_rightQ_before_leftQ': condition.IsRQuotaStickWithLQuota(),
        'is_empty': condition.IsSpace(SYMBOLS),
        'with_says': condition.WithSays(),
        'special_ends': condition.SpecialEnds()
    })

    nodes = attrdict.AttrDict({
        'do_cut': operation.Normal(SYMBOLS),
        'long_handler': operation.LongHandler(SYMBOLS, hard_max=hard_max),
        'short_handler': operation.ShortHandler(SYMBOLS),
        'init': operation.Indolent(SYMBOLS),
        'quota_handler': operation.Indolent(SYMBOLS),
        'end': operation.EndState(SYMBOLS)
    })
    return edges, nodes


# --- graph --- #
def long_short_cuter(**kwargs):
    edges, nodes = init_nodes(**kwargs)
    return {
        nodes.init: [
            {'edge': edges.is_end_state,
             'node': nodes.end},

            {'edge': edges.is_short_sentence,
             'node': nodes.init},

            {'edge': edges.is_long_sentence,
             'node': nodes.long_handler},

            {'edge': [edges.special_ends,
                      edges.is_leftQ_gt_1,
                      edges.is_rightQ_before_leftQ],
             'args': any,
             'node': nodes.do_cut},

            {'edge': edges.is_right_quota,
             'node': nodes.quota_handler},

            # -- normal cut -- #
            {'edge': [edges.is_end_symbol,
                      edges.is_bracket_close,
                      edges.is_book_close,
                      edges.is_quote_close],
             'args': all,
             'node': nodes.do_cut},

        ],
        nodes.quota_handler: [
            {'edge': edges.is_end_state,
             'node': nodes.end},

            {'edge': edges.is_left_quota,
             'node': nodes.do_cut},

            {'edge': edges.is_empty,
             'node': nodes.quota_handler},

            # -- normal cut -- #
            {'edge': [edges.is_end_symbol,
                      edges.is_bracket_close,
                      edges.is_book_close,
                      edges.is_quote_close],
             'args': all,
             'node': nodes.do_cut},

            {'edge': None,
             'node': nodes.init}
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
             'node': nodes.do_cut},
        ]
    }


def simple_cuter(**kwargs):
    edges, nodes = init_nodes(**kwargs)
    return {
        nodes.init: [
            {'edge': edges.is_end_state,
             'node': nodes.end},

            {'edge': [edges.special_ends,
                      edges.is_leftQ_gt_1,
                      edges.is_rightQ_before_leftQ],
             'args': any,
             'node': nodes.do_cut},

            {'edge': edges.is_right_quota,
             'node': nodes.quota_handler},

            # -- normal cut -- #
            {'edge': [edges.is_end_symbol,
                      edges.is_bracket_close,
                      edges.is_book_close,
                      edges.is_quote_close],
             'args': all,
             'node': nodes.do_cut},

        ],
        nodes.quota_handler: [
            {'edge': edges.is_end_state,
             'node': nodes.end},

            {'edge': edges.is_left_quota,
             'node': nodes.do_cut},

            {'edge': edges.is_empty,
             'node': nodes.quota_handler},

            # -- normal cut -- #
            {'edge': [edges.is_end_symbol,
                      edges.is_bracket_close,
                      edges.is_book_close,
                      edges.is_quote_close],
             'args': all,
             'node': nodes.do_cut},

            {'edge': None,
             'node': nodes.init}
        ],
        nodes.do_cut: [
            {'edge': edges.is_end_state,
             'node': nodes.end},

            {'edge': None,  # else 状态
             'node': nodes.init},
        ],
    }
