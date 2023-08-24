import base64
import re
import json
import requests


class SYLLABUS_API:
    def __init__(self, url, username, password):
        self.url_login = f'{url}/jsxsd/xk/LoginToXk'
        self.url_syllabus = f'{url}/jsxsd/xskb/xskb_list.do'
        self.username = username
        self.password = password

    headers = {
        'Host': 'qzjwxt.kjxy.nchu.edu.cn:800',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Referer': 'http://qzjwxt.kjxy.nchu.edu.cn:800/jsxsd/',
    }

    def get_logon_session(self):
        data = {
            'userAccount': '',
            'userPassword': '',
            'encoded': base64.b64encode(f'{self.username}%%%{self.password}'.encode()).decode(),
        }
        logon_session = requests.session()
        logon_session.post(self.url_login, headers=self.headers, data=data)
        return logon_session

    def get_syllabus(self, logon_session, time='2022-2023-2'):
        data = {
            'zc': '',
            'xnxq01id': time,
            'sfFD': '1'
        }
        response = logon_session.post(self.url_syllabus, headers=self.headers, data=data)
        return response.text

    def get_courses_info(self, xskb_list):
        result = re.findall(r'div id="(.*?)"([\s\S]*?)style="display: none;" class="kbcontent"[ >]([\s\S]*?)</div>',
                            str(xskb_list))
        courses_info = []

        for item in result:
            courses = re.findall(
                r'(.*?)<br/><font title=\'老师\'>(.*?)</font><br/><font title=\'周次\(节次\)\'>(.*?)</font><br/><font title=\'教室\'>(.*?)</font><br/>',
                item[2].replace('<span ><font color=\'red\'>&nbspP</font></span>', ''))

            for course, teacher, class_time, classroom in courses:
                course_info = [item[0], re.sub(r'<.*?>', '',
                                               course.replace('<br/>', '').replace('---------------------<br>',
                                                                                   '').replace('>', '')), teacher,
                               class_time, classroom]
                courses_info.append(course_info)

        with open('./syllabus.json', 'w') as jsonfile:
            json.dump(courses_info, jsonfile)


def get_today_class_schedule(week, day):
    with open('./syllabus.json', 'r') as jsonfile:
        courses_info = json.load(jsonfile)

    today_class_schedule = []
    today_output = '今日课表'

    for course_info in courses_info:
        if week in course_info[3] and day == course_info[0]:
            today_class_schedule.append(course_info)
    today_courses = sorted(today_class_schedule, key=lambda x: x[4])

    for course in today_courses:
        today_output += f'\n课程名称:{course[1]}\n任课老师:{course[2]}\n课程时间:{course[4]}\n上课教室:{course[5]}\n'

    return today_output


url = 'http://qzjwxt.kjxy.nchu.edu.cn:800'
username = '220208218'
password = '20040323'
time = '2022-2023-2'

nhky = SYLLABUS_API(url, username, password)
logon_session = nhky.get_logon_session()
syllabus = nhky.get_syllabus(logon_session=logon_session, time=time)
nhky.get_courses_info(syllabus)
print(get_today_class_schedule(2, 2))
