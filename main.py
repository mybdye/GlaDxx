"""GlaDxx自动签到脚本

支持多账户签到和多种推送通知方式
作者: DanielWu (mybdye)
"""

import os
import json
import base64
import logging
from typing import Dict, List, Optional
from urllib.parse import quote
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

REQUEST_DATA: Dict[str, str] = {
    "token": API_TOKEN
}

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
            
        headers = {"cookie": cookie_line.strip()}
        result = process_account(session, headers)
        results.append(result)
    
    # 发送聚合通知
    final_message = '\n\n---\n\n'.join(results)
    push_notification(final_message)

def process_account(session: requests.Session, headers: Dict[str, str]) -> str:
    """处理单个账户的签到
    
    Args:
        session: HTTP会话对象
        headers: 请求头
        
    Returns:
        处理结果字符串
    """
    try:
        # 执行签到
        checkin_response = session.post(
            url=CHECKIN_URL,
            headers=headers,
            data=REQUEST_DATA,
            timeout=30
        )
        checkin_response.raise_for_status()
        
        # 获取账户状态
        status_response = session.get(
            url=STATUS_URL,
            headers=headers,
            timeout=30
        )
        status_response.raise_for_status()
        
        # 解析响应数据
        checkin_data = checkin_response.json()
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
                
        return '\n'.join(result_lines)
        
    except KeyError as e:
        email_preview = headers.get("cookie", "")[:3]
        return f'email: {email_preview}***\nerror: 缺少必要字段 {e}\n请检查cookie或账户是否过期!'
        
    except json.JSONDecodeError as e:
        email_preview = headers.get("cookie", "")[:3]
        return f'email: {email_preview}***\nerror: JSON解析失败 {e}'
        
    except requests.RequestException as e:
        email_preview = headers.get("cookie", "")[:3]
        return f'email: {email_preview}***\nerror: 网络请求失败 {str(e)}'

if __name__ == "__main__":
    try:
        checkin()
    except Exception as e:
        logging.error(f"程序执行出错: {e}")
        raise
