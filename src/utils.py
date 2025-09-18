import datetime, json, os, sys
from typing import TypeVar
from PySide6.QtCore import QRect, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget

try: _base_path = sys._MEIPASS
except: _base_path = "."
def get_resourse(path: str) -> str:
    return os.path.join(_base_path, path)


def MyQFont(size: int, bold = False):
    font = QFont()
    font.setHintingPreference(QFont.PreferNoHinting)    # type: ignore
    font.setPointSize(size)
    if bold: font.setBold(True)
    return font


T = TypeVar('QWidget', bound="QWidget")
def WithFont(widget: T, font: QFont = MyQFont(9)) -> T:
    widget.setFont(font)
    return widget


def calculate_center_position(parent_rect: QRect, child_size: QSize) -> QRect:
    center_x = parent_rect.x() + (parent_rect.width() - child_size.width()) / 2
    center_y = parent_rect.y() + (parent_rect.height() - child_size.height()) / 2
    return QRect(int(center_x), int(center_y), child_size.width(), child_size.height())


def log(message: str):
    now = datetime.datetime.now()
    time_str = now.strftime("%H:%M:%S")
    print(f"[{time_str}] {message}")
    
    
def data_with_state(data: str, online: bool) -> str:
    state = "true" if online else "false"
    res = '{' + f'"state": {state}, "events": {data}' + '}'
    return res
    
    
def format_histroy(second: int, default: str) -> str:
    if second < 0: 
        return default
    if second < (60 * 60):
        return f"{second / 60}分钟前"
    if second < (60 * 60 * 24):
        return f"{second / 60 / 60}小时前"
    
    return f"{second / 60 / 60 / 24}天前"


def format_time() -> str:
    now = datetime.datetime.now()
    time_str = now.strftime("%H:%M")
    return time_str

def dumpEasliy(data: dict) -> str: 
    datas: list = data.get('value', [])
    new_list = []
    for data in datas:
        item = {}
        item['title'] = data.get("subject", "无标题")
        item['note'] = data.get("bodyPreview", "")
        item['start'] = data.get("start", {}).get("dateTime", None)
        item['end']   = data.get("end", {}).get("dateTime", None)
        
        if (item['start'] is None) or (item['end'] is None): continue
        
        if item['start'].endswith(".0000000"): item['start'] = item['start'].replace(".0000000", "Z")
        if item['end'].endswith(".0000000"): item['end'] = item['end'].replace(".0000000", "Z")
        
        new_list.append(item)
            
    return json.dumps(new_list, ensure_ascii=False)