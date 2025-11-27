import os

from src.utils import MyQFont, get_resourse, mkdir_not_exsits


class AppInfo:
    app_name = "小鱼日历"
    app_icon = get_resourse("assets/icon_mid.png")
    link = '<a href="https://github.com/syido/fish_calendar">项目地址</a>'
    license = '<a href="https://github.com/syido/fish_calendar/blob/main/docs/LICENSES.md">许可证</a>'
    cache_path = os.path.join(os.getenv('LOCALAPPDATA'), 'FishCalender')
    port = "717"
    
    AUTHORITY = "https://login.microsoftonline.com/common"
    SCOPES = ["Calendars.Read", "User.Read"]
    REDIRECT_PORT = "9999"
    REDIRECT_URI = "http://localhost:" + REDIRECT_PORT
    
mkdir_not_exsits(AppInfo.cache_path)

class AppUIStyle:
    class Font:
        default = MyQFont(9)
        head = MyQFont(11)
        big = MyQFont(13)
        small = MyQFont(8)
        
class ConstStr:
    class Connect:
        step1 = "点击“在浏览器打开”按钮或复制链接到浏览器，在打开的页面中登录账号并确认授权"
        simple_url = "https://not.found/404"
        step2 = "正在等待授权结果。如果授权成功仍无响应，也可以直接将含有 “localhost” 的链接复制到下面的文本框中："