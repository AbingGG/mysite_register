import hashlib,datetime,os
os.environ['DJANGO_SETTINGS_MODULE']='mysite_register.settings'
from . import models,forms
from django.shortcuts import render,redirect
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

# Create your views here.

def hash_code(s,sat="mysite_register"):
    s += sat    #应用的加密
    h  = hashlib.sha256()
    h.update(s.encode())#编译再用sha256更新
    return h.hexdigest()

def hash_comfirm_code(user):
    now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code=hash_code(user.name,now)
    models.Email_ConfirmString.objects.create(user=user,code=code)
    return code

def sen_email(code,to):
    subject="来自李桂彬django的项目测试"
    text_content="欢迎来到127.0.0.1:8000/confirm/?code={}的网站，请点击前面的网站进行邮箱的确认注册操作！"
    html_concent='<P>欢迎来到<a href="http://{}/confirm/?code={}" target=blank>www.baidu.com</a>的网站！</p>' \
                 '<p>请点击前面的网站在{}天内前进行邮箱的确认注册操作！</p>'.format('127.0.0.1:8000',code,settings.CONFIRM_DAYS)
    msg=EmailMultiAlternatives(subject,text_content,settings.EMAIL_HOST_USER,[to])
    msg.attach_alternative(html_concent,'text/html')
    msg.send()

def register(request):
    if request.session.get('is_login',None):
        return redirect("index")

    if request.method == "POST":
        register_forms=forms.RegisterForm(request.POST)
        message="请检查填写的内容"
        if register_forms.is_valid():#清除无效的字段
            username    = register_forms.cleaned_data['username']
            password    = register_forms.cleaned_data['password']
            is_password = register_forms.cleaned_data['is_password']
            email       = register_forms.cleaned_data['email']
            sex         = register_forms.cleaned_data['sex']


            if password != is_password:
                message="输入的密码不一致！"
                # print("1")
                return render(request, 'register/register.html', locals())

            else:
                same_username=models.User.objects.filter(name=username)
                if same_username:
                   message="你所填写的用户名已存在，请从新填写！"
                   return render(request, 'register/register.html', locals())

                same_email = models.User.objects.filter(email=email)
                if same_email:
                   message = "你所填写的邮箱已存在，请从新填写！"
                   return render(request, 'register/register.html', locals()) #locals为返回参数渲染

            if password==is_password:
                new_username         =models.User()
                new_username.name    =username
                new_username.password=hash_code(password)
                new_username.email   = email
                new_username.sex     = sex
                new_username.save()

                code=hash_comfirm_code(new_username)
                sen_email(code,email)
                message="请前往注册邮箱确认！"
                return render(request, 'register/confirm.html', locals())
    register_forms = forms.RegisterForm()
    return render(request,'register/register.html' ,locals())



def login(request):
    if request.method == "POST":
        if request.session.get("is_login",None):
            return redirect('/index/')
        login_forms=forms.UserForm(request.POST)
        message="验证码错误！"
        if login_forms.is_valid():
            username=login_forms.cleaned_data["username"]
            password=login_forms.cleaned_data["password"]
            try:
                user=models.User.objects.get(name=username)
                if not user.has_eamil_confirmed:
                    message='邮箱还没确认，请前往注册邮箱确认！'
                    return render(request, "register/login.html", locals())
                if user.password==hash_code(password):
                    request.session['is_login'] =True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('/index/')
                else:
                    message="密码错误！"
            except:
                message = "你所填写的用户名不存在，请从新填写！"
    login_forms=forms.UserForm()
    return render(request, "register/login.html",locals())

def index(request):
    pass
    return render(request,'register/index.html')

def logout(request):
    if not request.session.get("is_login",None):
        return redirect('/index/')
    else:
        request.session.flush()
        return redirect('/index/')

def user_confirm(request):
    # code = request.GET.get('code', None)
    # message = ''
    # try:
    #     confirm = models.Email_ConfirmString.objects.get(code=code)
    # except:
    #     message = '无效的确认请求!'
    #     return render(request, 'register/confirm.html', locals())
    #
    # c_time = confirm.c_time
    # now = datetime.datetime.now()
    # if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
    #     confirm.user.delete()
    #     message = '您的邮件已经过期！请重新注册!'
    #     return render(request, 'register/confirm.html', locals())
    # else:
    #     confirm.user.has_eamil_confirmed = True
    #     confirm.user.save()
    #     confirm.delete()
    #     message = '感谢确认，请使用账户登录！'
    #     return render(request, 'register/confirm.html', locals())
    code=request.GET.get("code",None)
    message=""
    try:
        # confirm=models.Email_ConfirmString.objects.get(code=code)
        confirm = models.Email_ConfirmString.objects.get(code=code)
    except:
        message="失效的确认请求,两秒后自动跳转。。。。。"
        return  render(request,'register/confirm.html',locals())
    # print(type(code))

    c_time=confirm.c_time#昨天
    now=datetime.datetime.now()#今天
    if now > c_time+datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message='邮件已经过期，请从新发送注册码，两秒后自动跳转。。。。'
        # print("邮件已经过期")
        return render(request, 'register/confirm.html', locals())
    else:
        confirm.user.has_eamil_confirmed=True
        confirm.user.save()
        confirm.delete()
        message="感谢确认，请使用账号登录！两秒后自动跳转。。。。"
        return render(request,'register/confirm.html',locals())

# def login(request):
#     if request.method == "POST":
#         username=request.POST.get("username",None)
#         password = request.POST.get("password",None)
#         message="账户密码都要填写"
#         if username and password:
#             username=username.strip()#去除前后多余的空格
#             try:
#                 user=models.User.objects.get(name=username)
#                 if user.password==password:
#                     return redirect('/index/')
#                 else:
#                     message="密码错误！"
#             except:
#                 message = "你所填写的用户名不存在，请从新填写！"
#         return render(request, "register/login.html",locals())
#     return render(request, "register/login.html")