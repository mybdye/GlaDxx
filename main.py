"""GlaDxx自动签到脚本

支持多账户签到和多种推送通知方式
作者: DanielWu (mybdye)
"""

import os
import json
import base64
import logging
from typing import Dict, List, Optional
from urllib.parse import quote, urlsplit
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def url_decode(encoded_str: str) -> str:
    """解码base64编码的URL字符串
    
    Args:
        encoded_str: base64编码的字符串
        
    Returns:
        解码后的字符串
    """
    try:
        padding = '=' * (4 - len(encoded_str) % 4)
        decoded_bytes = base64.b64decode(encoded_str + padding)
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        logging.error(f"URL解码失败: {e}")
        raise ValueError(f"无效的编码字符串: {encoded_str}")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# 环境变量配置
COOKIES: str = os.getenv('COOKIES', '')
# 可选：与登录网页端的浏览器保持一致；不配置时按服务端 loginDevice 自动重试
BROWSER_UA: Optional[str] = os.getenv('BROWSER_UA', '').strip() or None
BARK_TOKEN: Optional[str] = os.getenv('BARK_TOKEN')
PUSHDEER_KEY: Optional[str] = os.getenv('PUSHDEER_KEY')
TG_BOT_TOKEN: Optional[str] = os.getenv('TG_BOT_TOKEN')
TG_USER_ID: Optional[str] = os.getenv('TG_USER_ID')

def push_notification(message: str) -> None:
    """发送推送通知
    
    Args:
        message: 推送消息内容
    """
    logging.info(f"准备发送推送通知:\n{message}\n等待推送结果...")
    # Bark推送
    if BARK_TOKEN:
        try:
            bark_url = f'https://api.day.app/{BARK_TOKEN}'
            bark_title = 'GlaDxx-Checkin'
            encoded_message = quote(message, safe='')
            response = requests.get(
                url=f'{bark_url}/{bark_title}/{encoded_message}?group={bark_title}',
                timeout=10
            )
            response.raise_for_status()
            logging.info('✅ Bark推送成功!')
        except requests.RequestException as e:
            logging.error(f'❌ Bark推送失败: {e}')

    # PushDeer推送
    if PUSHDEER_KEY:
        try:
            pushdeer_url = 'https://api2.pushdeer.com/message/push'
            pushdeer_title = 'GlaDxx-Checkin'
            encoded_message = quote(message, safe='')
            params = {
                'pushkey': PUSHDEER_KEY,
                'text': pushdeer_title,
                'desp': encoded_message,
                'type': 'markdown'
            }
            response = requests.get(url=pushdeer_url, params=params, timeout=10)
            response.raise_for_status()
            logging.info('✅ PushDeer推送成功!')
        except requests.RequestException as e:
            logging.error(f'❌ PushDeer推送失败: {e}')

    # Telegram推送
    if TG_BOT_TOKEN and TG_USER_ID:
        try:
            tg_message = f'GlaDxx-Checkin\n\n{message}'
            tg_url = f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage'
            data = {
                'chat_id': TG_USER_ID,
                'text': tg_message
            }
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.post(url=tg_url, data=data, headers=headers, timeout=10)
            response.raise_for_status()
            logging.info('✅ Telegram推送成功!')
        except requests.RequestException as e:
            logging.error(f'❌ Telegram推送失败: {e}')
    
    logging.info('🔔 推送完成!')

# API配置
CHECKIN_URL: str = url_decode('aHR0cHM6Ly9nbGFkb3MuY2xvdWQvYXBpL3VzZXIvY2hlY2tpbg==')
STATUS_URL: str = url_decode('aHR0cHM6Ly9nbGFkb3MuY2xvdWQvYXBpL3VzZXIvc3RhdHVz')
API_TOKEN: str = url_decode('Z2xhZG9zLmNsb3Vk')
CHECKIN_ORIGIN: str = '{0.scheme}://{0.netloc}'.format(urlsplit(CHECKIN_URL))

REQUEST_DATA: Dict[str, str] = {
    "token": API_TOKEN
}

# 服务端会校验签到请求的 UA 平台与登录设备平台是否一致，
# 不一致时返回 code=4, reason=device-mismatch
PLATFORM_UA: Dict[str, str] = {
    'Windows': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'),
    'macOS': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'),
    'Linux': ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'),
    'iPhone': ('Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 '
               '(KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'),
    'iPad': ('Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 '
             '(KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'),
    'Android': ('Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'),
}

DEVICE_ALIASES: Dict[str, str] = {
    'mac': 'macOS',
    'macos': 'macOS',
    'mac os x': 'macOS',
    'macintosh': 'macOS',
    'windows': 'Windows',
    'linux': 'Linux',
    'iphone': 'iPhone',
    'ios': 'iPhone',
    'ipad': 'iPad',
    'ipados': 'iPad',
    'android': 'Android',
}

DEFAULT_USER_AGENT: str = BROWSER_UA or PLATFORM_UA['macOS']

def ua_for_device(device: Optional[str]) -> Optional[str]:
    """按服务端返回的 loginDevice 选择对应平台的 UA"""
    if not device:
        return None
    return PLATFORM_UA.get(DEVICE_ALIASES.get(device.strip().lower(), ''))

def build_headers(cookie: str, user_agent: str) -> Dict[str, str]:
    """构造与浏览器一致的请求头，UA 平台需与登录设备一致"""
    return {
        'cookie': cookie,
        'user-agent': user_agent,
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'origin': CHECKIN_ORIGIN,
        'referer': f'{CHECKIN_ORIGIN}/console/checkin',
    }

def request_checkin(session: requests.Session, cookie: str, user_agent: str) -> Dict:
    """发起一次签到请求并返回响应 JSON"""
    response = session.post(
        url=CHECKIN_URL,
        headers=build_headers(cookie, user_agent),
        data=REQUEST_DATA,
        timeout=30
    )
    response.raise_for_status()
    return response.json()

def create_session() -> requests.Session:
    """创建带有重试机制的HTTP会话
    
    Returns:
        配置好的requests.Session对象
    """
    session = requests.Session()
    
    # 配置重试策略
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def checkin() -> None:
    """执行签到操作并发送通知"""
    if not COOKIES.strip():
        logging.warning("⚠️ 未配置COOKIES环境变量")
        return
    
    session = create_session()
    results: List[str] = []
    
    for cookie_line in COOKIES.splitlines():
        if not cookie_line.strip():
            continue
            
        result = process_account(session, cookie_line)
        results.append(result)
    
    # 发送聚合通知
    final_message = '\n\n---\n\n'.join(results)
    push_notification(final_message)

def process_account(session: requests.Session, cookie_line: str) -> str:
    """处理单个账户的签到
    
    Args:
        session: HTTP会话对象
        cookie_line: 单行Cookie
        
    Returns:
        处理结果字符串
    """
    try:
        # 执行签到，UA 平台需与登录设备一致
        user_agent = DEFAULT_USER_AGENT
        checkin_data = request_checkin(session, cookie_line, user_agent)
        login_device = checkin_data.get('loginDevice')

        if checkin_data.get('code') == 4 and checkin_data.get('reason') == 'device-mismatch':
            retry_ua = ua_for_device(login_device)
            if retry_ua and retry_ua != user_agent:
                logging.warning(f'签到被判定为自动化(loginDevice={login_device})，改用对应平台 UA 重试')
                checkin_data = request_checkin(session, cookie_line, retry_ua)
                login_device = checkin_data.get('loginDevice')
            elif retry_ua:
                logging.error(f'设备平台为 {login_device}，UA 已匹配但服务端仍拒绝，请重新登录并更新 Cookie')
            else:
                logging.error(f'无法识别的登录设备平台 {login_device}，请配置 BROWSER_UA')

        # 获取账户状态
        status_response = session.get(
            url=STATUS_URL,
            headers={"cookie": cookie_line},
            timeout=30
        )
        status_response.raise_for_status()
        
        # 解析响应数据
        status_data = status_response.json()
        
        email_prefix = status_data["data"]["email"][:3]
        message = checkin_data["message"]
        traffic_gb = float(status_data["data"]["traffic"]) / (1024 ** 3)
        left_days = int(float(status_data["data"]["leftDays"]))
        
        result_lines = [
            f'email: {email_prefix}***',
            f'status: {message}',
            f'traffic: {traffic_gb:.2f} GB',
            f'leftDays: {left_days}'
        ]
        
        # 添加详细信息（如果存在）
        if "list" in checkin_data and checkin_data["list"]:
            detail = checkin_data["list"][0].get("detail", "")
            if detail:
                result_lines.append(detail)

        # 签到仍失败时补充服务端判定原因
        if checkin_data.get('code') == 4:
            reason = checkin_data.get('reason', 'unknown')
            result_lines.append(f'reason: {reason}' + (f' (loginDevice={login_device})' if login_device else ''))
            if reason == 'device-mismatch':
                result_lines.append('hint: 用登录网页端的浏览器重新复制完整 Cookie，或将 BROWSER_UA 设为该浏览器 UA')
                
        return '\n'.join(result_lines)
        
    except KeyError as e:
        email_preview = cookie_line[:3]
        return f'email: {email_preview}***\nerror: 缺少必要字段 {e}\n请检查cookie或账户是否过期!'
        
    except json.JSONDecodeError as e:
        email_preview = cookie_line[:3]
        return f'email: {email_preview}***\nerror: JSON解析失败 {e}'
        
    except requests.RequestException as e:
        email_preview = cookie_line[:3]
        return f'email: {email_preview}***\nerror: 网络请求失败 {str(e)}'

if __name__ == "__main__":
    try:
        checkin()
    except Exception as e:
        logging.error(f"程序执行出错: {e}")
        raise
