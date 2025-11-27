import clr, os
from src.utils import get_resourse

DLL = get_resourse("libs/FCForms/FCForms.dll")
clr.AddReference(DLL)

from FCForms import FCForms

__all__ = ["FCForms"]