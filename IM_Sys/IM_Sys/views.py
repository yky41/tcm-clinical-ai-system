
from django.shortcuts import render,redirect
from UserApp.models import User
from adminApp.models import Manager
from DoctorApp.models import Doctor
def test(request):
    return render(request,"user_")
def home(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('/login/')
    return render(request,"home.html",{})
#首先，它使用 request.session.get('is_login') 获取当前用户的登录状态。
#如果用户未登录（即 status 为 None 或 False），则重定向到登录页面 '/login/'。
#如果用户已登录（即 status 为 True），则渲染名为 "home.html" 的模板，并返回渲染结果。
#这个视图函数的作用是确保只有已登录的用户才能访问主页，如果用户未登录，则会被重定向到登录页面。
def login(request):
    message={"info":''}
    if request.method=="POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        print(username,password)
        if not username or not password:
            message["info"]="用户名或密码不能为空"
        else:
            # message["info"]="sussess"
            user_obj1 = User.objects.filter(user_name=username).first() #用户登陆从名为 User 的数据库模型中筛选出用户名与 username 变量匹配的所有用户对象。
            user_obj2 = Manager.objects.filter(manager_name=username).first()#管理员登陆
            user_obj3 = Doctor.objects.filter(doctor_name=username).first()#医生登陆
            user_obj,k=(user_obj1,"/user") if user_obj1 else (user_obj2,"/admin_sys") if user_obj2 else ( user_obj3,"/doctor")#从三种用户里选择
            if not user_obj:
                message["info"]="用户不存在"
            elif user_obj.states==0:
                message["info"]="您已被封号,或者还没同意您的账户请求，请联系管理员"
            elif user_obj.states==2:
                message["info"]="您的账户请求未通过，请重新注册"
            else:
                if password==user_obj.password:
                    request.session['is_login'] = True
                    request.session['username'] = username
                    request.session['uid'] = user_obj.uid
                    request.session['user_type'] = k
                    if k=="/doctor":
                        request.session['profile']=user_obj.profile
                    
                    return redirect(k+"/index/")
                else:
                    message["info"]="密码错误"


    
    return render(request,"login.html",message)
def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")
    request.session.flush()#是 Django 中用于清空当前会话数据的方法。调用这个方法会删除会话中的所有键值对，实现会话数据的清空，相当于用户注销或退出登录。
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/login/")#回到login页面
def register(request):
    message={"info":''}
    if request.method=="POST":
        username = request.POST.get("username")#都是在html中输入的
        password = request.POST.get("password")
        email= request.POST.get("email")
        role=request.POST.get("role")
        sex=request.POST.get('sex')
        age=request.POST.get('age')
        if role=="1":
            user=User()
            user.user_name=username
            user.password=password
            user.email=email
            user.user_sex=sex
            user.user_age=age
            user.save()
            return redirect("/login/")
        elif role=="2":
            doctor=Doctor()
            doctor.doctor_name=username
            doctor.password=password
            doctor.email=email
            doctor.doctor_sex=sex
            doctor.doctor_age=age
            doctor.save()

        elif role == "3":
            manage = Manager()
            manage.manager_name = username
            manage.password = password
            manage.email = email
            manage.manager_sex = sex
            manage.manager_age = age
            manage.save()

            return redirect("/login/")
        else:
            message={"info":'角色错误'}

    # print( request.POST)
    return render(request,"register.html",message)
def error(request):#错误页面
    return render(request,"error.html")