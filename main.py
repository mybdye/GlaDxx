# https://github.com/mybdye 🌟

import requests, base64, json, os
from urllib.parse import quote

#
def url_decode(s):
    return str(base64.b64decode(s + '=' * (4 - len(s) % 4))).split('\'')[1]

# 修改环境变量获取逻辑，增加可读性
cookiesList = os.getenv('COOKIES', '')
barkToken = os.getenv('BARK_TOKEN', '')
pushdeerKey = os.getenv('PUSHDEER_KEY', '')
tgBotToken = os.getenv('TG_BOT_TOKEN', '')
tgUserID = os.getenv('TG_USER_ID', '')

#
def push(body):
    print('- body:\n %s \n- waiting for push result' % body)
    # bark push
    if barkToken:
        barkurl = 'https://api.day.app/' + barkToken
        barktitle = 'Glaxxx-Checkin'
        encoded_body = quote(body, safe='')
        try:
            rq_bark = requests.get(url=f'{barkurl}/{barktitle}/{encoded_body}?isArchive=1')
            if rq_bark.status_code == 200:
                print('- bark push Done!')
            else:
                print('*** bark push fail! ***', rq_bark.content.decode('utf-8'))
        except requests.RequestException as e:
            print('*** bark push error! ***', str(e))

    # pushdeer
    if pushdeerKey:
        pushdeerurl = 'https://api2.pushdeer.com'
        pushdeertitle = 'Glaxxx-Checkin'
        encoded_body = quote(body, safe='')
        try:
            rq_pushdeer = requests.get(url=f'{pushdeerurl}/message/push?pushkey={pushdeerKey}&text={pushdeertitle}&desp={encoded_body}&type=markdown')
            if rq_pushdeer.status_code == 200:
                print('- pushdeer push Done!')
            else:
                print('*** pushdeer push fail! ***', rq_pushdeer.content.decode('utf-8'))
        except requests.RequestException as e:
            print('*** pushdeer push error! ***', str(e))

    # tg push
    if tgBotToken and tgUserID:
        body = 'Glaxxx-Checkin' + '\n\n' + body
        server = 'https://api.telegram.org'
        tgurl = server + '/bot' + tgBotToken + '/sendMessage'
        try:
            rq_tg = requests.post(tgurl, data={'chat_id': tgUserID, 'text': body}, headers={
                'Content-Type': 'application/x-www-form-urlencoded'})
            if rq_tg.status_code == 200:
                print('- tg push Done!')
            else:
                print('*** tg push fail! ***', rq_tg.content.decode('utf-8'))
        except requests.RequestException as e:
            print('*** tg push error! ***', str(e))
    print('- finish!')

#####
checkinUrl = url_decode('aHR0cHM6Ly9nbGFkb3Mucm9ja3MvYXBpL3VzZXIvY2hlY2tpbg==')
statusUrl = url_decode('aHR0cHM6Ly9nbGFkb3Mucm9ja3MvYXBpL3VzZXIvc3RhdHVz')
token = url_decode('Z2xhZG9zLm9uZQ==')
data = {
    "token": token
}

# 修改 checkin 函数，优化异常处理和字符串格式化
def checkin():
    body = []
    for cookies in cookiesList.splitlines():
        headers = {
            "cookie": cookies
        }
        try:
            r_checkin = requests.post(url=checkinUrl, headers=headers, data=data)
            r_status = requests.get(url=statusUrl, headers=headers, timeout=30)
            try:
                email = r_status.json()["data"]["email"][:3]
                message = r_checkin.json()["message"]
                traffic = float(r_status.json()["data"]["traffic"]) / 1024 / 1024 / 1024
                leftDays = int(float(r_status.json()["data"]["leftDays"]))
                s = f'email:{email}***\nstatus:{message}\ntraffic:{traffic:.2f} GB\nleftDays:{leftDays}'
                if "list" in r_checkin.json():
                    s += f'\ndetail:{r_checkin.json()["list"][0]["detail"]}'
            except KeyError as e:
                s = f'email:{email}***\nerror:{e}\nPlease check the cookie or account expiration date!'
            except json.JSONDecodeError as e:
                s = f'email:{email}***\nJSONDecodeError'
        except requests.RequestException as e:
            s = f'email:{cookies[:3]}***\nRequest Error: {str(e)}'
        body.append(s)
    pushbody = '\n- - -\n'.join(body)
    push(pushbody)

#
checkin()

# END