# -*- coding:utf-8 -*-
# CREATED BY: bohuai jiang 
# CREATED ON: 2020/8/12 11:17 AM
# LAST MODIFIED ON:
# AIM: 构建状态机
from typing import Set, Callable

from .abc import Criteria, Operation
from .sequence import StrSequence


class StateMachine:
    def __init__(self, graph: dict):
        self.graph = graph
        if not self.__is_valid_graph():
            raise Exception('invalid graph, please check if all nodes can connect to end_state')

        self.init_state = self.get_init_state()

    def get_init_state(self):
        for key in self.graph:
            if key.name == "Indolent":
                return key
        else:
            raise Exception('invalid graph, init_State not found')

    def __is_valid_graph(self) -> bool:
        for node in self.__get_all_nodes():
            try:
                for child in self.graph[node]:
                    if child['node'].name == 'EndState':
                        break
                else:
                    return False
            except:
                return False
        return True

    def __get_all_nodes(self) -> Set[Operation]:
        out = set()
        for node in self.graph:
            if node.name != 'EndState':
                out.add(node)
            for child in self.graph[node]:
                if child['node'].name != 'EndState':
                    out.add(child['node'])
        return out

    @staticmethod
    def __run_condition(info: dict, value: StrSequence):
        condition = info['edge']
        if isinstance(condition, Criteria) or isinstance(condition, Callable):
            return condition(value)
        elif isinstance(condition, list):
            out = []
            if info['args'] == all:
                quick = True
            else:
                quick = False

            for func in condition:
                if quick:
                    if not func(value):
                        return False
                else:
                    out.append(func(value))
            if quick:
                return True
            else:
                return info['args'](out)
        else:
            return True

    def run(self, value: StrSequence, verbose=False):
        # -- depth first search -- #
        vertex = self.init_state
        pre_v = vertex.name
        while vertex.name != 'EndState':
            # -- do operation -- #
            value = vertex(value)
            if verbose and vertex.name == 'Normal':
                try:
                    print(value.sentence_list[-1])
                except:
                    pass
            for child in self.graph[vertex]:
                child_node = child['node']
                if self.__run_condition(child, value):
                    vertex = child_node
                    if verbose:
                        print(value)
                        if vertex.name != pre_v:
                            print('<{}>:'.format(vertex.name))
                            pre_v = vertex.name
                    break
        value = vertex(value)
        return value
