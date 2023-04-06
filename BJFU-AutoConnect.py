import requests
import base64
from requests.sessions import RequestsCookieJar
import pywifi
import time

"""
检查是否存在 cookies.txt 文件
如果存在返回，并且第一行有内容返回 1，无内容返回 0
如果不存在返回 0，并创建 cookies.txt
"""


def checkCookie():
    hasCookies = 0
    try:
        f = open('cookies.txt', 'r')
        lines = f.readlines()
        if lines.count == 0:
            hasCookies = 0
        else:
            hasCookies = 1
        f.close()
    except FileNotFoundError:
        print('No cookies.txt, Create one')
        f = open('cookies.txt', 'x')
        hasCookies = 0
        f.close()
    return hasCookies


"""
截取字符串片段
"""


def cutString(str, s_start, s_end):
    # str       str
    # s_start   str
    # s_end     str
    # return    str
    pos_start = str.find(s_start)
    str_temp = str[pos_start + len(s_start):-1]
    pos_end = str_temp.find(s_end)
    return str_temp[:pos_end]


"""
保存 cookies 的值到 cookies.txt
"""


def saveCookies(cookies):
    # cookies   str
    f = open('cookies.txt', 'w')
    f.write(cookies)
    f.close()


"""
从 cookies.txt 中读取 cookies 的值
并返回一个 RequestsCookieJar 对象
"""


def getCookies():
    # return    RequestsCookiesJar
    cookies = RequestsCookieJar()
    f = open('cookies.txt', 'r')
    lines = f.readlines()
    value = lines[0].rstrip()
    cookies.set(name='JSESSIONID', value=value, path='/Self', domain='202.204.122.8')
    return cookies


"""
把 cookies 的值变成 RequestsCookiesJar 对象
"""


def makeCookies(str):
    # str       str
    # return    RequestsCookiesJar
    cookies = RequestsCookieJar()
    pos_start = str.find('jsessionid=')
    value = str[pos_start + len('jsessionid='): -1]
    cookies.set(name='JSESSIONID', value=value, path='/Self', domain='202.204.122.8')
    saveCookies(value)
    return cookies


"""
从 xyw.txt 中读取用户的账号密码，以元组形式返回
"""


def getUserTxt():
    # return    tuple(username, password)
    username = ''
    password = ''
    with open('xyw.txt', 'r') as f:
        lines = f.readlines()
        username = lines[0].rstrip()
        password = lines[1].rstrip()
    return username, password


"""
打印用户的信息
"""


def analysis(dashBoardText):
    # dashBoardText     str
    userFlow = cutString(dashBoardText, '"useFlow":', ',')
    leftFlow = cutString(dashBoardText, '"leftFlow":', ',')
    userCompany = cutString(dashBoardText, '"userCompany":"', '"')
    userGender = cutString(dashBoardText, '"userGender":"', '"')
    userGroup = cutString(dashBoardText, '"userGroupName":"', '"')
    userIdNumber = cutString(dashBoardText, '"userIdNumber":"', '"')
    userNum = cutString(dashBoardText, '"userName":"', '"')
    userPhone = cutString(dashBoardText, '"userPhone":"', '"')
    userRealName = cutString(dashBoardText, '"userRealName":"', '"')
    used = float(userFlow)
    left = float(leftFlow)
    uflow = ''
    lflow = ''
    if used > 1000:
        used = used / 1000
        uflow = str(used) + 'G'
    else:
        uflow = str(used) + 'M'
    if left > 1000:
        left = left / 1000
        lflow = str(left) + 'G'
    else:
        lflow = str(left) + 'M'
    print('姓名：' + userRealName)
    print('学号：' + userNum)
    print('已用流量：' + uflow)
    print('剩余流量：' + lflow)
    print('套餐：' + userGroup)
    print('性别：' + userGender)
    print('班级：' + userCompany)
    print('身份证号码：' + userIdNumber)
    print('手机号码：' + userPhone)


def login():
    # 获取分配的 IP 地址
    r = requests.get('http://10.1.1.10/')
    text = r.text
    ip = cutString(text, 'v46ip=\'', '\'')

    # 生成提交的表单信息
    username, password = getUserTxt()
    pass_base = base64.b64encode(password.encode()).decode()
    dataToGet = {
        'callback': 'dr1004',
        'login_method': 1,
        'user_account': username,
        'user_password': pass_base,
        'wlan_user_ip': ip,
        'wlan_user_ipv6': '',
        'wlan_user_mac': '000000000000',
        'wlan_ac_ip': '',
        'wlan_ac_name': '',
        'jsVersion': '4.1.3',
        'terminal_type': 1,
        'type': 1,
        'lang': 'en',
        'v': 1218,
    }
    # 获取登录的 url
    r = requests.get('http://10.1.1.10:801/eportal/portal/custom/auth', params=dataToGet)
    url = cutString(r.text, '"self_auth_url":"', '"')
    url = url.replace('\\', '')

    hasCookies = checkCookie()
    if hasCookies == 0:
        # 没有 cookies 时，保存一个cookies
        r = requests.get(url)
        cookies = makeCookies(r.url)
    else:
        # 当 cookies 已存在，直接登录
        cookies = getCookies()
        r = requests.get(url, cookies=cookies)

    # 打印用户信息
    analysis(dashBoardText=r.text)


def isConnected():
    if ifaces.status() == pywifi.const.IFACE_CONNECTED:
        print("成功连接到校园网")
        return True
    else:
        print("失败，请查看是否在校园网范围内")
        return False


if __name__ == "__main__":
    wifi = pywifi.PyWiFi()  # 创建一个无线对象
    ifaces = wifi.interfaces()[0]  # 取一个无限网卡
    print(ifaces.name())  # 输出无线网卡名称
    ifaces.disconnect()  # 断开网卡连接
    time.sleep(0.5)  # 缓冲0.5秒

    profile = pywifi.Profile()  # 配置文件
    profile.ssid = "bjfu-wifi"  # wifi名称
    ifaces.remove_all_network_profiles()  # 删除其他配置文件
    tmp_profile = ifaces.add_network_profile(profile)  # 加载配置文件
    ifaces.connect(tmp_profile)  # 连接
    time.sleep(1)  # 等待1秒后看下是否成功连接了
    if not isConnected():
        time.sleep(2)  # 若未成功，等待2秒后再看下是否成功连接了
        isConnected()
    login()
