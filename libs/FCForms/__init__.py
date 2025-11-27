import clr, os
from src.utils import get_resourse
from typing import Callable, TypeVar

DLL = get_resourse("libs/FCForms/FCForms.dll")
clr.AddReference(DLL)

from FCForms import FCForms
from System import Action

__all__ = ["FCForms"]


def _readyThen(func: Callable):
    FCForms._ReadyThen(Action(func))
FCForms.ReadyThen = _readyThen

def _homeBA(button: FCForms.Button, func: Callable):
    FCForms._HomeBA(Action(func))
FCForms.HomeBA = _homeBA