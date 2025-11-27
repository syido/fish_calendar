import datetime as dt
import logging
import queue
import requests
import threading
import time
from queue import Queue

import pystray
from PIL import Image
from PySide6.QtCore import QObject, Signal, Slot, QThread, QCoreApplication, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, \
    QHBoxLayout, QGroupBox, QSpacerItem, QMessageBox, QApplication
from flask import Flask, Response
from flask_cors import CORS
from werkzeug.serving import make_server

from src.app_config import AppInfo, AppUIStyle
from src.auth_manage import AuthManage
from src.connect_box import ConnectBox
from src.utils import *
from src.version import VersionBox

from libs.FCForms import FCForms


class FishCalenderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(AppInfo.app_name)
        self.resize(QSize(300, 500))
        self.am = None
        self.task_queue = Queue(2)
        self.update_queue = Queue()
        self.setFont(AppUIStyle.Font.default)
        self.setWindowIcon(QIcon(AppInfo.app_icon))
        self.init_widget()
        self.main_ui()
        self.blind_event()
        self.setup_thread()
        self.tray = None
        
    
    def closeEvent(self, event):
        self.hide()
        event.ignore()
        
        
    def init_widget(self):
        self.name_label = QLabel("正在检查同步状态...")
        self.connect_button = QPushButton("连接")
        self.connect_button.setEnabled(False)
        self.sync_state_label = QLabel("🏵️正在等待验证")
        self.sync_res_label = WithFont(QLabel("未同步"), AppUIStyle.Font.small)
        self.sync_date_label = WithFont(QLabel(""), AppUIStyle.Font.small)
        self.sync_button = QPushButton("立即同步")
        self.server_res = WithFont(QLabel("🏵️正在等待运行"))
        self.server_date = WithFont(QLabel(" "), AppUIStyle.Font.small)
        self.reset_button = WithFont(QPushButton("重启"))
        self.reset_button.setEnabled(False)
        
        def init():
            FCForms.HomeT(FCForms.Label.lAccount, "正在检查同步状态...")
            FCForms.HomeT(FCForms.Button.bExit, "连接")
        
        FCForms.ReadyThen(init)
        
        
    def blind_event(self):
        self.connect_button.clicked.connect(self.on_connect_clicked)
        self.sync_button.clicked.connect(self.on_sync_clicked)
        self.reset_button.clicked.connect(self.on_reset_clicked)
        
    
    def main_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        layout.addLayout(self.account_ui())
        layout.addSpacerItem(QSpacerItem(0, 20))
        layout.addLayout(self.server_ui())
        
        layout.addStretch()
        
    
    def account_ui(self) -> QVBoxLayout:
        layout = QVBoxLayout() 
        layout.addWidget(WithFont(QLabel("同步账号"), AppUIStyle.Font.head))
        
        def account(self) -> QHBoxLayout:
            layout = QHBoxLayout()
            layout.addWidget(self.name_label)
            layout.addStretch()
            layout.addWidget(self.connect_button)
            return layout
        
        def sync(self) -> QGroupBox:
            box = QGroupBox()
            layout = QHBoxLayout()
            box.setLayout(layout)
            
            layout_mini = QVBoxLayout()
            layout.addLayout(layout_mini)
            
            layout_mini.addWidget(self.sync_state_label)
            layout_mini.addWidget(self.sync_res_label)
            # layout_mini.addWidget(self.sync_date)
            
            layout.addStretch()
            layout.addWidget(self.sync_button)
            
            return box
        
        layout.addLayout(account(self))
        layout.addWidget(sync(self))
        
        return layout
    
    
    def server_ui(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.addWidget(WithFont(QLabel("本地服务器"), AppUIStyle.Font.head))
        
        def server(self) -> QGroupBox:
            box = QGroupBox()
            layout = QHBoxLayout()
            box.setLayout(layout)
            
            layout_mini = QVBoxLayout()
            layout.addLayout(layout_mini)
            
            layout_mini.addWidget(self.server_res)
            layout_mini.addWidget(self.server_date)
            
            layout.addStretch()
            layout.addWidget(self.reset_button)
            
            return box
        
        layout.addWidget(server(self))
        return layout
    
    
    def setup_thread(self):
        cal_cache = os.path.join(AppInfo.cache_path, 'calender.json')
        first_data = ""
        if os.path.exists(cal_cache):
            with open(cal_cache, 'r', encoding='utf-8') as file:
                first_data = file.read()
        
        self.sync_worker = SyncWorker(self.task_queue)
        self.tray_worker = TrayWorker(self.task_queue)
        self.serv_worker = ServerWorker(self.update_queue, first_data)
        self.sync_thread = MyQThread('sync')
        self.tray_thread = MyQThread('tray')
        self.serv_thread = MyQThread('serv')
        self.sync_worker.moveToThread(self.sync_thread)
        self.tray_worker.moveToThread(self.tray_thread)
        self.serv_worker.moveToThread(self.serv_thread)
        
        self.sync_worker.finished.connect(self.sync_thread.quit)
        self.tray_worker.finished.connect(self.tray_thread.quit)
        self.sync_worker.finished.connect(lambda: print("finish了"))
        self.sync_thread.started.connect(self.sync_worker.run)
        self.tray_thread.started.connect(self.tray_worker.run)
        self.serv_thread.started.connect(self.serv_worker.run)
        
        # 自定义槽
        self.sync_worker.check_res_sign.connect(self.on_check_res)
        self.sync_worker.auth_manage_sin.connect(self.on_set_auth_manage)
        self.sync_worker.sync_state_sign.connect(self.on_sync_state)
        
        self.tray_worker.signal.connect(self.on_tray_signal)
        
        self.serv_worker.state_signal.connect(self.on_server_signal)
        
        self.sync_thread.start()
        self.tray_thread.start()
        self.serv_thread.start()
    
    
    def on_connect_clicked(self):
        if '退出' in self.connect_button.text():
            reply = QMessageBox.question(None, "退出登录", f"是否确定退出登录（程序将重新启动）",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No: return
            QApplication.instance().exit(42)
            
            return
        
        rect = calculate_center_position(self.geometry(), QSize(400, 300))
        if self.am is None:
            log("还没创建权限管理器")
            return

        self.update_queue.put("stop")
        self.version_dialog = ConnectBox(self, rect, self.am)
        log("打开了验证窗口")
        res = self.version_dialog.exec()
        self.task_queue.put("check")
        self.task_queue.put("sync")
        del self.version_dialog
    
    def on_sync_clicked(self):
        self.task_queue.put("sync")
        self.sync_button.setEnabled(False)
        
    def on_reset_clicked(self):
        log("重启放入任务队列")
        self.update_queue.put(None)
        self.reset_button.setEnabled(False)

    @Slot(bool, str)
    def on_check_res(self, res, name):
        self.connect_button.setEnabled(True)
        if res:
            self.connect_button.setText("退出")
            self.name_label.setText(name)
            self.sync_button.setEnabled(True)
        else:
            self.connect_button.setText("连接")
            self.name_label.setText("登录一个账号")
            self.sync_button.setEnabled(False)
        log("检查了账号的状态")

    @Slot(AuthManage)
    def on_set_auth_manage(self, am: AuthManage):
        self.am = am
        
    @Slot(int, int, str)
    def on_sync_state(self, state: int, num: int, err: str):
        # log("on_sync_state触发")
        match state:
            case -1:
                self.sync_state_label.setText("🌸" + err)
                self.sync_res_label.setText(format_time() + ' · 发生错误')
                self.sync_button.setEnabled(True)
            case 0:
                self.sync_state_label.setText("🏵️正在同步")
                self.sync_res_label.setText("现在 · 正连接到服务器")
            case 1:
                self.sync_state_label.setText("🍀同步成功")
                self.sync_res_label.setText(format_time() + f' · 共{num}条日程')
                self.update_queue.put("")
                self.sync_button.setEnabled(True)
                
    @Slot(int)
    def on_tray_signal(self, command: bool):
        match command:
            case 0:
                self.task_queue.put(None)
                self.update_queue.put(None)
                if not self.tray_worker.icon is None:
                    self.tray_worker.icon.stop()
                self.sync_thread.wait()
                self.serv_thread.quit()
                QCoreApplication.instance().quit()
            case 1: 
                self.show()
            case 2:
                self.version_dialog = VersionBox()
                self.version_dialog.exec()
            
            
    @Slot(int)
    def on_server_signal(self, state):
        match state:
            case -1:
                self.server_res.setText("🌸桌面连接断开")
                self.server_date.setText(f"{format_time()} · 等待重连")
            case 0:
                self.reset_button.setEnabled(True)
                self.server_res.setText("🍀向桌面推送成功")
                self.server_date.setText(f"{format_time()} · 缓存数据")
            case 1:
                self.server_res.setText("🍀向桌面推送成功")
                self.reset_button.setEnabled(True)
                self.server_date.setText(f"{format_time()} · 新数据")
    
    
class SyncWorker(QObject):
    auth_manage_sin = Signal(AuthManage)
    check_res_sign = Signal(bool, str)
    sync_state_sign = Signal(int, int, str)
    finished = Signal()
    
    def __init__(self, task_queue: Queue, sync_time: int = 600):
        """不建议小于5秒的时间间隔"""
        self.task_queue = task_queue
        self.sync_time = sync_time
        self.am = None
        
        super().__init__()
        
        
    def run(self):
        init_fail = True
        last_sync_time = -1
        
        while init_fail:
            try:
                self.am = AuthManage()
                self.auth_manage_sin.emit(self.am)
                init_fail = False
            except requests.exceptions.ConnectionError as e:
                log(f"服务器连接失败，5秒后重试：{e}")
                time.sleep(5)
            except Exception as e: 
                raise(e)
            
        self.task_queue.put("check")
        log("同步线程开始运行")
        
        while True:
            # 正常刷新分支
            if self.task_queue.qsize() == 0:
                if time.time() - last_sync_time >= self.sync_time:
                    log("自动同步中：")
                    news = self.sync()
                    last_sync_time = time.time()
                time.sleep(0.5)
                continue
            
            task = self.task_queue.get()
            
            # 停止分支
            if task is None: break
                
            # 刷新分支
            if task == "check":
                log("同步线程检查缓存")
                check_res, name = self.am.check_cache()
                self.check_res_sign.emit(check_res, name)
                if not check_res:
                    last_sync_time = time.time()
                    while not self.task_queue.qsize() == 0:
                        self.task_queue.get()
                    log("等待登录账号")
                else: 
                    log(f'账户：{name}')
                
            # 立即同步分支
            if task == "sync":
                log("主动同步中：")
                news = self.sync()
        
        log("同步线程主动退出")
        # self.finished.emit()
        QThread.currentThread().quit()
       
       
    def sync(self) -> bool:
        self.sync_state_sign.emit(0, 0, "")
        now = dt.datetime.now(dt.timezone.utc)
        start_date = now - dt.timedelta(days=30)
        end_date = now + dt.timedelta(days=120)
        
        headers = {
            'Authorization': f'Bearer {self.am.get_token()}',
            'Content-Type': 'application/json'
        }
        params = {
            'startDateTime': start_date.isoformat(),
            'endDateTime': end_date.isoformat(),
        }
        
        endpoint = f"https://graph.microsoft.com/v1.0/me/calendarView"
        
        try:
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()
            length = len(result.get('value', []))
            log(f"同步了{length}条记录")
            
            file_path = os.path.join(AppInfo.cache_path, "calender.json")
            with open(file_path, 'w', encoding='utf-8') as file:
                s = dumpEasliy(result)
                file.write(s)
            log(f"写入了{s[:50]}...")
            
            self.sync_state_sign.emit(1, length, "")    
            return True
        
        except FileNotFoundError:
            mkdir_not_exsits(AppInfo.cache_path)
            self.task_queue.put("check")
        except requests.exceptions.HTTPError as err:
            err_str = "似乎是Token过期，即将刷新"
            log(f"{err_str}: {err}")  # 在这里访问 err
            self.task_queue.put("check")
        except requests.exceptions.ConnectionError as err:
            err_str = "连接错误"
            log(f"在与日程服务器同步时{err_str}: {err}")
        except requests.exceptions.Timeout as err:
            err_str = "请求超时"
            log(f"在与日程服务器同步时{err_str}: {err}")
        except Exception as err:
            err_str = "未知错误"
            log(f"在与日程服务器同步时{err_str}: {err}")
        
        self.sync_state_sign.emit(-1, 0, err_str)
        time.sleep(10)
        self.task_queue.put("sync")
        return False


class ServerWorker(QObject):
    state_signal = Signal(int)
    
    def __init__(self, update_queue: queue.Queue, first_data):
        super().__init__()
        self.update_queue = update_queue
        self.file_path = os.path.join(AppInfo.cache_path, 'calender.json')
        self.is_new_data = False
        self.data = first_data
        self.port = AppInfo.port
        self._srv = None
        self.should_run = True

    def run(self):
        while self.should_run:
            _log = logging.getLogger('werkzeug')
            _log.setLevel(logging.ERROR)
            flask_app = Flask("桌面服务器")
            CORS(flask_app)
            self.flask_app = flask_app
            
            def return_data():
                if not self.data is None:
                    self.state_signal.emit(1 if self.is_new_data else 0)
                    log("重新向桌面推送")
                    data = data_with_state(self.data, self.is_new_data)
                    yield f"data: {data}\n\n"
                
                try:
                    while True:
                        if self.update_queue.qsize() == 0:
                            time.sleep(5)
                            yield ": keep-alive\n\n"
                            continue
                            
                        task = self.update_queue.get_nowait()
                        if task == "stop":
                            log("本地服务器暂停，等待账号刷新")
                            while True:
                                if self.update_queue.qsize() != 0: break
                                time.sleep(0.1)
                            log("本地服务器恢复")
                        elif task is None:
                            log("将关闭桌面服务器") 
                            threading.Thread(target=lambda: self._srv.shutdown() if self._srv else None, daemon=True).start()
                            break
                        else:
                            with open(self.file_path, 'r', encoding='utf-8') as file:
                                self.data = file.read()
                            self.is_new_data = True
                            log("向桌面推送了")
                            self.state_signal.emit(1 if self.is_new_data else 0)
                            data = data_with_state(self.data, self.is_new_data)
                            yield f"data: {data}\n\n"
                            
                except queue.Empty:
                    log("队列似乎有一个小错误")
                except GeneratorExit:
                    log("SSE 连接已断开")
                except Exception as e:
                    log(f"SSE 连接发生未知错误: {e}")
                finally: self.state_signal.emit(-1)
                time.sleep(1)
                    
            @flask_app.route('/getdata', methods=['GET'])
            def get_data():
                return Response(return_data(), mimetype='text/event-stream')

            @flask_app.route('/nutshell')
            def nutshell():
                log("桌面服务器收到连接测试")
                return "I could be bounded in a nutshell and count myself a king of infinite space."
    
            try:
                # 使用 make_server 创建可控的 WSGI server
                self._srv = make_server('127.0.0.1', self.port, flask_app)
                log(f"桌面服务器将在 http://127.0.0.1:{self.port} 中开放")
                self._srv.serve_forever()
            except Exception as e:
                log(f"桌面服务器发生错误: {e}")

            log("桌面服务器线程结束")
            self._srv = None
    
    def shutdown(self):
        log("将关闭桌面服务器")
        self.should_run = False
        threading.Thread(target=lambda: self._srv.shutdown() if self._srv else None, daemon=True).start()

class TrayWorker(QObject):
    signal = Signal(int)
    finished = Signal()
    
    def __init__(self, task_queue: queue.Queue):
        self.task_queue = task_queue
        self.icon = None
        super().__init__()
        
    def on_exit(self):
        self.signal.emit(0)
        
    def on_show(self):
        self.signal.emit(1)
        
    def on_about(self):
        self.signal.emit(2)
        
    def on_cache(self):
        os.startfile(AppInfo.cache_path)
    
    def update_now(self):
        self.task_queue.put("sync")
    
    def _set_auto_start(self, enable: bool, app_name: str) -> bool:
        try:
            import winreg
            if enable: value = f'"{sys.executable}" -s'
            else: value = None

            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE)
            if enable:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, value)
                log("已开启开机启动")
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
                log("已关闭开机启动")
            winreg.CloseKey(key)
            return True
        except Exception as e:
            log(f"设置开机启动失败: {e}")
            return False

    def _is_auto_start_enabled(self, item=None) -> bool:
        try:
            import winreg
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, AppInfo.app_name)
            winreg.CloseKey(key)
            if not value:
                return False
            v = value.strip().strip('"')
            has_path = sys.executable in value or sys.executable == v
            has_flag = "-s" in value.split()
            return bool(has_path and has_flag)
        except Exception:
            return False

    def toggle_auto_start(self, icon, item):
        name = AppInfo.app_name
        currently = self._is_auto_start_enabled()
        ok = self._set_auto_start(not currently, name)
        try:
            if hasattr(self, "icon") and self.icon:
                update = getattr(self.icon, "update_menu", None)
                if callable(update):
                    update()
        except Exception:
            pass    
        
    def run(self):
        menu = (
            pystray.MenuItem('立即同步', self.update_now),
            # pystray.MenuItem('配置文件', lambda: None),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('开机启动', self.toggle_auto_start, checked=self._is_auto_start_enabled),
            pystray.MenuItem('打开缓存路径', self.on_cache),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('关于' + AppInfo.app_name, self.on_about),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('打开窗口', self.on_show, default=True),
            pystray.MenuItem('退出', self.on_exit)
        )
        
        icon_image = Image.open(AppInfo.app_icon)
        self.icon = pystray.Icon(AppInfo.app_name, icon_image, AppInfo.app_name, menu)
        self.icon.run(setup=None)
        # self.finished.emit()
        # TODO
        # 不知道为什么就是不能用finished.emit()方法退出
        QThread.currentThread().quit()
