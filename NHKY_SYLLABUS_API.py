import base64
import re
import json
import requests


class SYLLABUS_API:
    def __init__(self, url, username, password):  # 初始化教务系统平台,账号和密码
        self.url_login = str(url) + '/jsxsd/xk/LoginToXk'
        self.url_syllabus = str(url) + '/jsxsd/xskb/xskb_list.do'

        self.username = str(username)
        self.password = str(password)

    headers = {
        'Host': 'qzjwxt.kjxy.nchu.edu.cn:800',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Referer': 'http://qzjwxt.kjxy.nchu.edu.cn:800/jsxsd/',
    }

    def get_logon_session(self):  # 登入用户,返回登入session(logon_session)
        username = self.username
        password = self.password
        data = {
            'userAccount': '',
            'userPassword': '',
            'encoded': base64.b64encode(username.encode()).decode() + '%%%' + base64.b64encode(
                password.encode()).decode(),
        }
        logon_session = requests.session()
        logon_session.post(self.url_login, headers=self.headers, data=data)
        return logon_session

    def get_syllabus(self, logon_session, time='2022-2023-2'):  # 查询总课表(返回以text)默认为总周数 time 为学期
        data = {
            'zc': '',
            'xnxq01id': str(time),
            'sfFD': '1'
        }
        response = logon_session.post(self.url_syllabus, headers=self.headers, data=data)
        return response.text

    def get_courses_info(self, xskb_list):  # 正则表达课表并保存课程信息为json文件,这样设计是为了在教务网环境打不开的情况下可以直接通过本地文件读取到总课表信息

        # 正则表达式过滤出课程信息,此过滤规则由 ChatGPT 生成,如果课表有问题,注意测试更新规则
        result = re.findall(r'div id="(.*?)"([\s\S]*?)style="display: none;" class="kbcontent"[ >]([\s\S]*?)</div>',
                            str(xskb_list))
        courses_info = []
        for item in result:
            courses = re.findall(
                r'(.*?)<br/><font title=\'老师\'>(.*?)</font><br/><font title=\'周次\(节次\)\'>(.*?)</font><br/><font title=\'教室\'>(.*?)</font><br/>',
                item[2].replace('<span ><font color=\'red\'>&nbspP</font></span>', ''))
            for course, teacher, class_time, classroom in courses:
                course_info = [item[0],
                               re.sub(r'<.*?>', '',
                                      course.replace('<br/>', '').replace('---------------------<br>', '').replace('>',
                                                                                                                   '')),
                               teacher, class_time, classroom]
                courses_info.append(course_info)

        # 过滤出的信息以 day(星期几) course(课程) teacher(老师) class_time(上课时间) classroom(上课教室) 为列表
        # 进一步转化课程信息,以便 json 格式保存，以及进一步优化信息

        for i in range(len(courses_info)):
            day = courses_info[i][0][-3]
            course = courses_info[i][1]
            teacher = courses_info[i][2]

            weeks, class_time = courses_info[i][3].split('(周)')
            week_list = []
            weeks = weeks.replace('[', '').replace(']', '')  # 去除"[]"符号
            # 检查是否含有逗号分隔的多个周数
            if ',' in weeks:
                weeks = weeks.split(',')
            else:
                weeks = [weeks]

            for week in weeks:
                # 检查是否为范围表示
                if '-' in week:
                    start, end = map(int, week.split('-'))
                    week_list.extend(range(start, end + 1))
                else:
                    week_list.append(int(week))

            class_time_mapping = {
                '[01-02节]': '08:30 ~ 09.55',
                '[03-04节]': '10:05 ~ 11:30',
                '[05-06节]': '13:20 ~ 14:45',
                '[07-08节]': '14:55 ~ 16:20',
                '[09-10节]': '19:20 ~ 21:55',
                '[01-02-03-04节]': '08:30 ~ 11:30',
                '[05-06-07-08节]': '13:20 ~ 16:20'
            }
            class_time = class_time_mapping.get(class_time, class_time)

            classroom = courses_info[i][4]

            courses_info[i] = [int(day), str(course), str(teacher), list(week_list), str(class_time), str(classroom)]

        # 保存优化后的课程信息到本地
        with open('./syllabus.json', 'w') as jsonfile:
            json.dump(courses_info, jsonfile)


def get_today_class_schedule(week, day):
    # 读取 课表信息 到列表
    with open('./syllabus.json', 'r') as jsonfile:
        courses_info = json.load(jsonfile)

    today_class_schedule = []
    today_output = '今日课表'

    # 遍历课表 匹配 week 和 day
    for course_info in courses_info:
        if int(week) in course_info[3] and int(day) == course_info[0]:
            today_class_schedule.append(course_info)
    today_courses = sorted(today_class_schedule, key=lambda x: x[4])

    for course in today_courses:
        today_output += '\n课程名称:' + course[1] + '\n任课老师:' + course[2] + '\n课程时间:' + course[
            4] + '\n上课教室:' + course[5] + '\n'

    return today_output


# user.ini
# 说明：部分英语用词不严谨，请自行修改代码
url = 'http://qzjwxt.kjxy.nchu.edu.cn:800' # 教务平台网址
username = '********' # 用户名
password = '********' # 密码
time = '2022-2023-2'  # 规则为 学年开始-学年结束-学期数

# demo
nhky = SYLLABUS_API(url, username, password)  # 教务平台用户名与密码
logon_session = nhky.get_logon_session()  # 获取登入session
syllabus = nhky.get_syllabus(logon_session=logon_session, time=time)  # 获取总课表
nhky.get_courses_info(syllabus)  # 保存课程信息到本地(方便教务网打不开也能获取课表信息)
print(get_today_class_schedule(2, 2))  # 打印课表信息
