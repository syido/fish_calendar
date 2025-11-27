import sys, shutil, argparse

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QIcon

from src.fish_calender import FishCalenderApp
from src.utils import log, wait_process, start_myself, get_resourse
from src.app_config import AppInfo, AppUIStyle
from src.dialogs import Dialog

from libs.FCForms import FCForms


def delete_cache():
    log("将要删除缓存")
    while True:
        try:
            shutil.rmtree(AppInfo.cache_path)
            log("删除成功")
        except Exception as e:
            log(f"删除时发生错误：{e}")
            reply = Dialog.confirm(None, "发生错误", f"退出登录时发生错误：{e}，是否重试？")
            if reply == Dialog.Yes:
                continue
        break


def main():
    # 解析参数
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', type=int, help="等待程序的pid")
    parser.add_argument('-s', action='store_true', help="静默启动")
    parser.add_argument('-d', action='store_true', help="退出账号")
    args, _ = parser.parse_known_args()
    
    # 先启动应用
    app = QApplication(sys.argv)
    FCForms.Run()
    # app.setFont(AppUIStyle.Font.default)
    
    # 清理缓存部分
    if args.d:
        if args.w is None:
            raise argparse.ArgumentTypeError("删除缓存必须有等待pid参数 (-w [pid])")
        w_res = wait_process(args.w)
        if not w_res:
            log("上一个进程不肯结束")
            Dialog.alarm(None, "上一个进程不肯结束", "可能需要手动删除缓存")
        delete_cache()
        QApplication.setWindowIcon(QIcon(get_resourse("assets/icon.ico")))
        
    # 再启动窗口
    window = FishCalenderApp()
    
    if not args.s: 
        window.show()
    
    # 退出部分
    exit_code = app.exec()
    if exit_code == 42:
        start_myself()
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()