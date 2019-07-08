import os
from django.core.mail import EmailMultiAlternatives

os.environ['DJANGO_SETTINGS_MODULE']='mysite_register.settings'

if __name__ == '__main__':
    subject,from_email,to="来自李桂彬django的项目测试","liguibin21@sina.com","1069684210@qq.com"
    text_content="欢迎来到127.0.0.1:8000/index/的网站，请点击前面的网站进行邮箱的确认注册操作！"
    html_concent='<P>欢迎来到<a href="127.0.0.1:8000/index/" target=blank>127.0.0.1:8000/index/</a>的网站，请点击前面的网站进行邮箱的确认注册操作！</p>'
    msg=EmailMultiAlternatives(subject,text_content,from_email,[to])
    msg.attach_alternative(html_concent,'text/html')
    msg.send()