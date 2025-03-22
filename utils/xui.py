import requests
import json
from config.settings import XUI_PANELS
from datetime import datetime, timedelta

class XUIPanel:
    def __init__(self, url, username, password):
        self.url = url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.token = None

    def login(self):
        """ورود به پنل"""
        try:
            response = self.session.post(
                f"{self.url}/login",
                data={
                    "username": self.username,
                    "password": self.password
                }
            )
            if response.status_code == 200:
                self.token = response.json().get('token')
                return True
            return False
        except Exception as e:
            print(f"خطا در ورود به پنل: {str(e)}")
            return False

    def create_config(self, name, volume, duration):
        """ایجاد کانفیگ جدید"""
        if not self.token:
            if not self.login():
                return None

        try:
            expiry_date = datetime.now() + timedelta(days=duration)
            response = self.session.post(
                f"{self.url}/api/inbounds",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "up": 0,
                    "down": 0,
                    "total": volume * 1024 * 1024 * 1024,  # تبدیل گیگابایت به بایت
                    "remark": name,
                    "enable": True,
                    "expiryTime": int(expiry_date.timestamp() * 1000),
                    "listen": "",
                    "port": 0,
                    "protocol": "vless",
                    "settings": {
                        "clients": [
                            {
                                "id": self._generate_uuid(),
                                "flow": "",
                                "email": name,
                                "limitIp": 0,
                                "totalGB": volume
                            }
                        ],
                        "decryption": "none",
                        "fallbacks": []
                    },
                    "streamSettings": {
                        "network": "tcp",
                        "security": "none",
                        "tcpSettings": {
                            "header": {
                                "type": "none"
                            }
                        }
                    }
                }
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"خطا در ایجاد کانفیگ: {str(e)}")
            return None

    def delete_config(self, config_id):
        """حذف کانفیگ"""
        if not self.token:
            if not self.login():
                return False

        try:
            response = self.session.delete(
                f"{self.url}/api/inbounds/{config_id}",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"خطا در حذف کانفیگ: {str(e)}")
            return False

    def get_config_stats(self, config_id):
        """دریافت آمار کانفیگ"""
        if not self.token:
            if not self.login():
                return None

        try:
            response = self.session.get(
                f"{self.url}/api/inbounds/{config_id}/stats",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"خطا در دریافت آمار کانفیگ: {str(e)}")
            return None

    def _generate_uuid(self):
        """تولید UUID تصادفی"""
        import uuid
        return str(uuid.uuid4())

def get_available_panel():
    """دریافت اولین پنل در دسترس"""
    for panel in XUI_PANELS:
        xui = XUIPanel(panel['url'], panel['username'], panel['password'])
        if xui.login():
            return xui
    return None 