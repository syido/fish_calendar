import json, msal, os, threading
from typing import Optional
from urllib.parse import urlparse, parse_qs
from src.app_config import AppInfo
from src.app_key import AppKey
from src.utils import log


class AuthManage:
    def __init__(self) -> None:
        self.cache = msal.SerializableTokenCache()
        self.lock = threading.Lock()
        self.token = None

        self.cache_path = os.path.join(AppInfo.cache_path, "token.bin")
        if os.path.exists(self.cache_path):
            log(f"发现缓存文件并加载")
            self._load_cache()

        with self.lock:
            self.app = msal.ConfidentialClientApplication(
                client_id=AppKey.CLIENT_ID,
                client_credential=AppKey.CLIENT_SECRET,
                authority=AppInfo.AUTHORITY,
                token_cache=self.cache
            )
            self.flow: Optional[dict] = None
            self.state = 0
        
        
    def _load_cache(self):
        """[线程安全] 从文件加载缓存"""
        with self.lock:
            self.cache.deserialize(open(self.cache_path, "r", encoding='utf-8').read())
        
        
    def _update_cache(self):
        """[线程安全] 缓存更新后保存到文件和类"""
        with self.lock:
            log("想要保存缓存")
            has_state_changed = self.cache.has_state_changed
            cache_str = self.cache.serialize()
            if has_state_changed:
                log(f"缓存已更新，保存到 {self.cache_path}")
                with open(self.cache_path, "w", encoding='utf-8') as f:
                    f.write(cache_str)
            cache = json.loads(cache_str)
            account, access = cache.get("Account", [{}]), cache.get("AccessToken", [{}])
            for _, a in account.items():
                self.username = a.get("username", "未知账号"); break
            for _, a in access.items():
                self.token = a.get("secret", None); break
             
                 
    def get_token(self) -> Optional[str]:
        """[线程安全] 获取token"""
        with self.lock:
            res = self.token
        return self.token
    
    
    def _get_email(self) -> str:
        """[线程安全] 获取用户名"""
        with self.lock:
            res = self.username
        return self.username
        
    
    def check_cache(self) -> tuple[bool, str]:
        last_state = self.state
        try:
            if last_state == 0: self.state = 1
            accounts = self.app.get_accounts()
            if not accounts:
                log("缓存中无账户信息，需要手动登录。")
                return False, "" 
            
            log("缓存中发现账户，正在尝试获取令牌")
            result = self.app.acquire_token_silent(AppInfo.SCOPES, account=accounts[0])
            
            if result and "access_token" in result:
                log("获取令牌成功！")
                self._update_cache()
                return True, self._get_email() 
            else:
                log("静默获取令牌失败，需要手动登录。")
                return False, "" 
            
        except Exception as e:
            log(e)
            self.state = last_state
            return True, None
            
        
    def get_url(self) -> str | None:
        if self.state == 0:
            log("需要先更新缓存")
            return None
        
        self.flow = self.app.initiate_auth_code_flow(scopes=AppInfo.SCOPES, redirect_uri=AppInfo.REDIRECT_URI)
        log("获取请求授权链接：")
        log(self.flow["auth_uri"])
        
        self.state = 2
        return self.flow["auth_uri"]

    
    def check_url(self, url:str) -> tuple[bool, str]:
        if self.state != 2:
            log("需要先获取链接")
            return False, ""
        
        try:
            query_params = parse_qs(urlparse(url).query)
            unpacked_params = {key: value[0] for key, value in query_params.items()}
            
            result = self.app.acquire_token_by_auth_code_flow(self.flow, auth_response=unpacked_params)

            if "access_token" in result:
                log("手动授权成功，已获取令牌！")
                self._update_cache()
                return True, self._get_email()
            else:
                error_desc = result.get("error_description", "未知错误")
                log(f"使用URL换取令牌失败: {error_desc}")
                return False, error_desc
        except Exception as e:
            log(f"处理回调URL时发生异常: {e}")
            return False, str(e)