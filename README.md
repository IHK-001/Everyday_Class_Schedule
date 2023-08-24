## 使用方法：
```python
import NHKY_SYLLABUS_API

# user.ini
# 说明：部分英语用词不严谨，请自行修改代码
url = 'http://qzjwxt.kjxy.nchu.edu.cn:800'
username = '********'
password = '********'
time = '2022-2023-2'  # 规则为 学年开始-学年结束-学期数

# demo
nhky = NHKY_SYLLABUS_API(username, password)  # 登入用户名与密码
logon_session = nhky.get_logon_session()  # 获取登入session
syllabus = nhky.get_syllabus(logon_session=logon_session, time=time)  # 获取总课表
nhky.get_courses_info(syllabus)  # 保存课程信息到本地(方便教务网打不开也能获取课表信息)
print(get_today_class_schedule(2, 2))  # 打印课表信息
```
## 参数说明与修改:
【注】本代码未包含报错反馈，正则表达式部分需要自行修改
```python
url = 'http://qzjwxt.kjxy.nchu.edu.cn:800'
username = '********' # 用户名
password = '********' # 用户密码
time = '2022-2023-2'  # 规则为 学年开始-学年结束-学期数

nhky = NHKY_SYLLABUS_API(username, password)  # 登入用户名与密码
logon_session = nhky.get_logon_session()  # 获取登入session
syllabus = nhky.get_syllabus(logon_session=logon_session, time=time)  # 获取总课表(必须同时调用logon_session，确保能够登入)
nhky.get_courses_info(syllabus)  # 保存课程信息到本地(方便教务网打不开也能获取课表信息)

get_today_class_schedule # 从本地的课表json 获取课表信息，返回值为str，请调用前确保已更新信息到本地
# 如果本地已经有课表信息且不需要更新的情况下可以直接调用该函数
```
本校调用只需按照上面的配置即可
其它学校需要修改教务系统的url链接
## 错误:
```
如果没返回课表则有以下问题:
1.IP被封禁
第二天再尝试获取信息
2.链接错误
需要手动修改教务系统链接
2.课表过滤规则有问题
过滤规则仅适用（南昌航空大学科技学院）
```

请多次调试


