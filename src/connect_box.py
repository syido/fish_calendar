import logging
import queue
import requests
import threading

from PySide6.QtCore import Qt, QRect, QSize, QObject, Signal, Slot, QThread, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, \
    QHBoxLayout, QGroupBox, QSpacerItem, QLineEdit, QDialog
from flask import Flask, request
from werkzeug.serving import make_server

from src.app_config import AppInfo, AppUIStyle, ConstStr
from src.auth_manage import AuthManage
from src.utils import log


class ConnectBox(QDialog):
    def __init__(self, parent, rect: QRect, am: AuthManage):
        super().__init__(parent=parent)
        self.parent = parent
        self.am = am
        self.setWindowTitle("连接到服务器")
        self.setGeometry(rect)
        self.setFixedSize(QSize(rect.width(), rect.height()))
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setFont(AppUIStyle.Font.default)
        self.init_widget()
        self.init_ui()
        self.blind_event()
        self.setup_auth_thread()
        
        
    def init_widget(self):
        self.url_text = QLineEdit(ConstStr.Connect.simple_url, readOnly=True)
        self.res_text = QLineEdit("")
        self.state_info = QLabel("🏵️正在等待授权")
        self.state_info.setAlignment(Qt.AlignCenter)    # type: ignore
        self.copy_button = QPushButton("复制")
        self.open_url_button = QPushButton("在浏览器中打开")
        self.summit_button = QPushButton("提交")
        self.cancel_button = QPushButton("取消")
        self.ok_button = QPushButton("确定")
        
        self.cancel_button.setEnabled(False)
        self.ok_button.setEnabled(False)
        
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        layout.addWidget(QLabel(ConstStr.Connect.step1, wordWrap=True))
        
        link_layout = QHBoxLayout()
        link_layout.addWidget(self.url_text)
        link_layout.addWidget(self.copy_button)
        link_layout.addWidget(self.open_url_button)
        layout.addLayout(link_layout)
        
        layout.addSpacerItem(QSpacerItem(0, 20))
        layout.addWidget(QLabel(ConstStr.Connect.step2, wordWrap=True))
        res_layout = QHBoxLayout()
        res_layout.addWidget(self.res_text)
        res_layout.addWidget(self.summit_button)
        layout.addLayout(res_layout)
        
        layout.addSpacerItem(QSpacerItem(0, 20))
        state_box = QGroupBox()
        state_layout = QVBoxLayout()
        state_box.setLayout(state_layout)
        state_layout.addWidget(self.state_info)
        layout.addWidget(state_box)
        
        layout.addStretch()
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        layout.addLayout(button_layout)
        
        
    def setup_auth_thread(self): 
        parent = self.parent
        parent.dialog_auth_thread = QThread()
        parent.dialog_auth_thread.setObjectName("a")
        parent.dialog_serv_thread = QThread()
        parent.dialog_serv_thread.setObjectName("b")
        
        self.auth_task_queue = queue.Queue()
        parent.dialog_auth_worker = AuthWorker(self.am, self.auth_task_queue)
        parent.dialog_serv_worker = AuthServer(self.auth_task_queue)
        parent.dialog_auth_worker.moveToThread(parent.dialog_auth_thread)
        parent.dialog_serv_worker.moveToThread(parent.dialog_serv_thread)
        
        parent.dialog_auth_worker.url_poster.connect(self.auth_url_slot)
        parent.dialog_auth_worker.result.connect(self.auth_res_slot)
        parent.dialog_serv_worker.already_signal.connect(self.auth_serv_already)
        
        parent.dialog_auth_worker.finished.connect(parent.dialog_auth_thread.quit)
        parent.dialog_serv_worker.finished.connect(parent.dialog_serv_thread.quit)
        parent.dialog_auth_thread.started.connect(parent.dialog_auth_worker.run)
        parent.dialog_serv_thread.started.connect(parent.dialog_serv_worker.run)
        parent.dialog_auth_thread.finished.connect(parent.dialog_auth_thread.deleteLater)
        parent.dialog_serv_thread.finished.connect(parent.dialog_serv_thread.deleteLater)
        
        parent.dialog_auth_thread.start()
        parent.dialog_serv_thread.start()
        
        
    def blind_event(self):
        self.summit_button.clicked.connect(self.on_check_clicked)
        self.copy_button.clicked.connect(self.on_copy_clicked)
        self.open_url_button.clicked.connect(self.on_open_url_clicked)
        self.cancel_button.clicked.connect(lambda: (self.shutdown(),self.reject()))
        self.ok_button.clicked.connect(lambda: (self.shutdown(), self.accept()))
        
    
    def shutdown(self):
        self.auth_task_queue.put(None)
        shutdown_url = 'http://localhost:' + AppInfo.REDIRECT_PORT + '/shutdown'
        def temp_func():
            try: requests.get(shutdown_url)
            except: log("似乎没能正确关闭服务器")
        threading.Thread(target=temp_func, daemon=True).start()
    
    
    def on_check_clicked(self):
        text = self.res_text.text()
        self.auth_task_queue.put(text)
        log(f"提交了一段文本")
    
    @Slot(str)
    def auth_url_slot(self, url: str):
        self.url_text.setText(url)
        self.url_text.setCursorPosition(0)
    
    @Slot(bool, str)
    def auth_res_slot(self, res: bool, name: str):
        if res:
            self.res_text.setText("认证成功")
            self.res_text.setEnabled(False)
            self.state_info.setText(f"🍀已连接到{name}")
            self.summit_button.setEnabled(False)
            self.ok_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
            self.shutdown()
        else:
            self.state_info.setText(f"🌸连接错误")
    
    def auth_serv_already(self):
        self.cancel_button.setEnabled(True)
        
    def on_copy_clicked(self):
        QApplication.instance().clipboard().setText(self.url_text.text())
        
    def on_open_url_clicked(self):
        url = QUrl(self.url_text.text())
        QDesktopServices.openUrl(url)

    
class AuthWorker(QObject):
    url_poster = Signal(str)
    result = Signal(bool, str)
    finished = Signal()
    
    def __init__(self, am: AuthManage, task_queue: queue.Queue):
        self.am = am
        super().__init__()
        self.task_queue = task_queue
        
    def run(self):
        url = self.am.get_url()
        self.url_poster.emit(url)
        
        suc = False
        while not suc:
            log("准备检查传回的链接")
            url = self.task_queue.get()
            if url is None: 
                break
            suc, name = self.am.check_url(url)
            self.result.emit(suc, name)
        
        log("授权检查已关闭")
        self.finished.emit()
        
            
class AuthServer(QObject):
    already_signal = Signal()
    finished = Signal()
    
    def __init__(self, task_queue: queue.Queue):
        super().__init__()
        self.task_queue = task_queue
        self.port = AppInfo.REDIRECT_PORT
        self._srv = None

    def run(self):
        _log = logging.getLogger('werkzeug')
        _log.setLevel(logging.ERROR)
        flask_app = Flask("授权服务器")
        self.flask_app = flask_app

        @flask_app.route('/', methods=['GET'])
        @flask_app.route('/<path:path>', methods=['GET'])
        def catch_all(path='/'):
            full_url = request.url
            log(f"授权服务器取得回调URL")
            self.task_queue.put(full_url)
            return "<h1><h1>🐟🐟 已提交认证，你可以关闭这个标签页了</h1>"

        @flask_app.route('/shutdown', methods=['POST', 'GET'])
        def shutdown():
            log("将关闭授权服务器")
            threading.Thread(target=lambda: self._srv.shutdown() if self._srv else None, daemon=True).start()
            return("撒优拉哪")
            # raise KeyboardInterrupt

        @flask_app.route('/nutshell')
        def nutshell():
            return "I could be bounded in a nutshell and count myself a king of infinite space."
  
        try:
            # 使用 make_server 创建可控的 WSGI server
            self._srv = make_server('127.0.0.1', self.port, flask_app)
            log(f"授权服务器将在 http://127.0.0.1:{self.port} 中开放")
            self.already_signal.emit()
            # flask_app.run(host='localhost', port=self.port, debug=False)
            self._srv.serve_forever()
        except Exception as e:
            log(f"授权服务器发生错误: {e}")

        log("授权服务器线程结束")
        self._srv = None
        self.finished.emit()