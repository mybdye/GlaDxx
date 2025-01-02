# https://github.com/mybdye 🌟

import requests, base64, json, os
from urllib.parse import quote

#
def url_decode(s):
    return str(base64.b64decode(s + '=' * (4 - len(s) % 4))).split('\'')[1]

#
def push(body):
    print('- body:\n %s \n- waiting for push result' % body)
    # bark push
    if barkToken == '':
        print('*** No BARK_KEY ***')
    else:
        barkurl = 'https://api.day.app/' + barkToken
        barktitle = 'Glaxxx-Checkin'
        barkbody = quote(body, safe='')
        rq_bark = requests.get(url=f'{barkurl}/{barktitle}/{barkbody}?isArchive=1')
        if rq_bark.status_code == 200:
            print('- bark push Done!')
        else:
            print('*** bark push fail! ***', rq_bark.content.decode('utf-8'))

    # pushdeer
    if pushdeerKey == '':
        print('*** No PUSHDEER_KEY ***')
    else:
        pushdeerurl = 'https://api2.pushdeer.com'
        pushdeertitle = 'Glaxxx-Checkin'
        barkbody = quote(body, safe='')
        rq_pushdeer = requests.get(url=f'{pushdeerurl}/message/push?pushkey={pushdeerKey}&text={pushdeertitle}&desp={barkbody}&type=markdown')
        if rq_pushdeer.status_code == 200:
            print('- pushdeer push Done!')
        else:
            print('*** pushdeer push fail! ***', rq_pushdeer.content.decode('utf-8'))
            
    # tg push
    if tgBotToken == '' or tgUserID == '':
        print('*** No TG_BOT_TOKEN or TG_USER_ID ***')
    else:
        body = 'Glaxxx-Checkin' + '\n\n' + body
        server = 'https://api.telegram.org'
        tgurl = server + '/bot' + tgBotToken + '/sendMessage'
        rq_tg = requests.post(tgurl, data={'chat_id': tgUserID, 'text': body}, headers={
            'Content-Type': 'application/x-www-form-urlencoded'})
        if rq_tg.status_code == 200:
            print('- tg push Done!')
        else:
            print('*** tg push fail! ***', rq_tg.content.decode('utf-8'))
    print('- finish!')


#
try:
    cookiesList = os.environ['COOKIES']
except:
    # 本地调试用
    cookiesList = ''
try:
    barkToken = os.environ['BARK_TOKEN']
except:
    # 本地调试用
    barkToken = ''
try:
    pushdeerKey = os.environ['PUSHDEER_KEY']
except:
    # 本地调试用
    pushdeerKey = ''
try:
    tgBotToken = os.environ['TG_BOT_TOKEN']
except:
    # 本地调试用
    tgBotToken = ''
try:
    tgUserID = os.environ['TG_USER_ID']
except:
    # 本地调试用
    tgUserID = ''

#####
checkinUrl = url_decode('aHR0cHM6Ly9nbGFkb3Mucm9ja3MvYXBpL3VzZXIvY2hlY2tpbg==')
statusUrl = url_decode('aHR0cHM6Ly9nbGFkb3Mucm9ja3MvYXBpL3VzZXIvc3RhdHVz')
token = url_decode('Z2xhZG9zLm9uZQ==')
data = {
    "token": token
}

#
def checkin():
    body = []
    for cookies in cookiesList.splitlines():
        # print(cookies)
        headers = {
            "cookie": cookies
        }
        r_checkin = requests.post(url=checkinUrl, headers=headers, data=data)
        r_status = requests.get(url=statusUrl, headers=headers, timeout=30)
        try:
            s = 'email:%s***\nstatus:%s\ntraffic:%.2f GB\nleftDays:%s\ndetail:%s' % (r_status.json()["data"]["email"][:3], r_checkin.json()["message"], float(r_status.json()["data"]["traffic"]/1024/1024/1024), int(float(r_status.json()["data"]["leftDays"])), r_checkin.json()["list"][0]["detail"])
        except KeyError as e:
            s = 'email:%s***\nerror:%s\nPlease check the cookie or account expiration date!' % (r_status.json()["data"]["email"][:3], e)
        except json.JSONDecodeError as e:
            s = 'email:%s***\nJSONDecodeError' % (r_status.json()["data"]["email"][:3], e)
        else:
            s = 'email:%s***\nstatus:%s\ntraffic:%.2f GB\nleftDays:%s' % (r_status.json()["data"]["email"][:3], r_checkin.json()["message"], float(r_status.json()["data"]["traffic"]/1024/1024/1024), int(float(r_status.json()["data"]["leftDays"])))
        body.append(s)
    pushbody = ''
    for i in range(len(body)):
        if i + 1 != len(body):
            pushbody += body[i] + '\n- - -\n'
        else:
            pushbody += body[i]
    #print(pushbody)
    push(pushbody)

#
checkin()

# END
