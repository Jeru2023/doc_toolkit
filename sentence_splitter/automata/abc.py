# -*- coding:utf-8 -*-
# CREATED BY: bohuai jiang
# CREATED ON: 2020/8/4 2:52 PM
# LAST MODIFIED ON:
# AIM: automata abstract class
from abc import ABC, abstractmethod

from .sequence import StrSequence


class Criteria(ABC):
    def __init__(self, name: str, symbols: dict, reverse: bool = False, ):
        self.name = name
        self.revers = reverse
        self.symbols = symbols

    @abstractmethod
    def accept(self, state: StrSequence) -> bool:
        assert (0)

    def __call__(self, state: StrSequence):
        if self.revers:
            return not self.accept(state)
        else:
            return self.accept(state)


class Operation(ABC):
    def __init__(self, name: str, symbols: dict):
        self.name = name
        self.symbols = symbols

    @abstractmethod
    def operate(self, state: StrSequence) -> StrSequence:
        assert (0)

    def __call__(self, state: StrSequence) -> StrSequence:
        return self.operate(state)

    def init_var(self):
        pass