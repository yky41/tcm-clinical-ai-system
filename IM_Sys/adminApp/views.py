
from django.shortcuts import render,redirect
from adminApp.models import Manager
from DoctorApp.models import Doctor,Department
from BlogApp.models import News,Post,Comment
from UserApp.models import User,Visit,Userinfo,PEinfo
from django.http import HttpResponse
from django.http import HttpResponseRedirect,JsonResponse

def login_role_auth(fn):
    def wrapper(request,*args,**kwargs):
        if request.session.get('is_login', False) and request.session.get('user_type')=="/admin_sys" :
            return fn(request,*args,*kwargs)
        else:
            # 获取用户当前访问的url，并传递给/user/login/
            next = request.get_full_path() 
            request.session["is_login"]=False
            red = HttpResponseRedirect("/login/")
            return red
    return wrapper

@login_role_auth
def change_pwd(request):#个人中心 修改密码
    massage={"info":''}
    if request.method=="POST":
        old_pwd=request.POST.get("old_pwd")
        new_pwd=request.POST.get("new_pwd")
        if old_pwd==new_pwd:
            massage={"info":'新密码和原密码一致',"res":0}
        else:
            user=Manager.objects.filter(uid=request.session.get('uid')).first()
            if user.password!=old_pwd:
                massage={"info":'原密码不正确',"res":1}
            else:
                user.password=new_pwd
                user.save()
                massage={"info":'密码修改成功',"res":2}
        return JsonResponse(massage) 
    else:
        return render(request,"admin_pwd.html",massage)
def personal_info(request):#个人中心 个人信息
    if request.method=="GET":
        manager=Manager.objects.filter(uid=request.session.get('uid')).first()
        return render(request,"admin_index.html",{"user":manager})
    elif request.method=="POST":
        manager=Manager.objects.filter(uid=request.session.get('uid')).first()
        manager_name=request.POST.get('manager_name')
        email=request.POST.get('email')
        manager_sex=request.POST.get('manager_sex')
        manager_age=request.POST.get('manager_age')
        department = request.POST.get('department')
        manager.manager_name=manager_name
        manager.email=email
        manager.manager_sex=manager_sex
        manager.manager_age=manager_age
        manager.department = department
        manager.save()
        return redirect("/admin_sys/index/")

@login_role_auth
def user_manage(request):#用户管理
    user_id=request.GET.get("uid")
    if request.method=="GET" and not user_id:
        users=User.objects.all()
        return render(request,"patient_manage.html",{"users":users})
    elif user_id:
        user=User.objects.filter(uid=user_id).first()
        user.states=0
        user.save()
        return redirect("/admin_sys/user_manage/")

        return redirect("/admin_sys/user_manage/")
    if request.method=="POST":
        user_id=request.POST


def user_manage1(request):
    user_id = request.GET.get("uid")
    if request.method == "GET" and not user_id:
        users = User.objects.all()
        return render(request, "patient_manage.html", {"users": users})
    elif user_id:
        user = User.objects.filter(uid=user_id).first()
        user.states = 1
        user.save()
        return redirect("/admin_sys/user_manage/")

        return redirect("/admin_sys/user_manage/")
    if request.method == "POST":
        user_id = request.POST

@login_role_auth
def doctor_manage(request):  # 医生管理 增删查改
    uid = request.GET.get("uid")

    if request.method == "GET" and not uid:  # 查询所有医生
        doctors = Doctor.objects.all()
        return render(request, "doctor_manage.html", {"doctors": doctors})

    elif uid:  # 处理传入的uid
        type = request.GET.get("type")

        doctor = Doctor.objects.filter(uid=uid).first()
        if type in ["1", "2"]:  # 处理通过/驳回操作
            doctor.states = int(type)

            doctor.save()

        if type == "10" and request.method == "POST":  # 处理编辑操作
            doctor.doctor_name = request.POST.get("doctor_name")
            doctor.email = request.POST.get("email")
            doctor.doctor_sex = request.POST.get("doctor_sex")
            doctor.doctor_age = request.POST.get("doctor_age")
            doctor.deid = request.POST.get("deid")
            doctor.hospital = request.POST.get("hospital")
            doctor.role = request.POST.get("role")
            doctor.good_at = request.POST.get("good_at")
            doctor.save()

        return redirect("/admin_sys/doctor_manage/")

    elif request.method == "POST":
        type = request.POST.get("type")
        if type == "add":
            pass
        elif type == "change":
            pass
        elif type == "delete":
            uid = request.POST.get("uid")
            doctor = Doctor.objects.filter(uid=uid).first()
            doctor.delete()

        return redirect("/admin_sys/doctor_manage/")  # 添加这一行来确保在POST请求中有返回值

    return redirect("/admin_sys/doctor_manage/")  # 添加这一行来确保在其他情况下也有返回值




def edit_doctor_info(request):
    if request.method == 'POST':
        uid = request.GET.get('uid')
        departments = Department.objects.all()
        if not uid:
            return HttpResponse("Invalid request. UID is missing in the POST data.")

        try:
            doctor = Doctor.objects.get(uid=uid)
        except Doctor.DoesNotExist:
            return HttpResponse("Doctor matching query does not exist.")

        doctor.doctor_name = request.POST.get("doctor_name")
        doctor.email = request.POST.get("email")
        doctor.doctor_sex = request.POST.get("doctor_sex")
        doctor.doctor_age = request.POST.get("doctor_age")
        deid = request.POST.get('deid')
        doctor.deid = Department.objects.filter(id=deid).first()
        doctor.hospital = request.POST.get('hospital')
        doctor.good_at = request.POST.get('good_at')
        doctor.title = request.POST.get('title')
        doctor.save()
        return redirect('/admin_sys/doctor_manage/')  # 重定向到医生管理页面
    else:
        uid = request.GET.get('uid')
        departments = Department.objects.all()
        if not uid:
            return HttpResponse("Invalid request. UID is missing in the GET data.")

        try:
            doctor = Doctor.objects.get(uid=uid)
        except Doctor.DoesNotExist:
            return HttpResponse("Doctor matching query does not exist.")

        return render(request, 'edit_doctor_info.html', {'doctor': doctor,'departments':departments})


def user_manage2(request):#用户管理
    if request.method=="POST":
        user_id=request.GET.get("uid")
        visit = Visit.objects.all()
        if not user_id:
            return HttpResponse("Invalid request. UID is missing in the POST data.")
        try:
            user= User.objects.get(uid=user_id)

        except User.DoesNotExist:
            return HttpResponse("user matching query does not exist.")
        user.user_name = request.POST.get("user_name")
        user.password = request.POST.get("password")
        user.email = request.POST.get("email")
        user.user_sex = request.POST.get("user_sex")
        user.user_age = request.POST.get("user_age")


        user.save()
        return redirect('/admin_sys/user_manage/')  # 重定向到医生管理页面

    else:
        user_id = request.GET.get('uid')
        visit = Visit.objects.all()
        if not user_id:
            return HttpResponse("Invalid request. UID is missing in the GET data.")

        try:
            user = User.objects.get(uid=user_id)
        except User.DoesNotExist:
            return HttpResponse("User matching query does not exist.")

        return render(request, 'edit_user_info.html', {'user': user,'visit':visit})

# class Department(models.Model):#所属科室
#     id=models.AutoField(primary_key=True)
#     d_name= models.CharField(max_length=255)#科室名称
#     introduce=models.TextField(null=True)#科室介绍




def keshi(request):
    departments = Department.objects.all()

    for department in departments:
        department.doctors = Doctor.objects.filter(deid__d_name=department.d_name)

    return render(request, 'keshi_manage.html', {'departments': departments})

def add_department(request):
    if request.method == 'POST':
        d_name = request.POST.get('d_name')
        introduce = request.POST.get('introduce')
        if d_name and introduce:
            Department.objects.create(d_name=d_name, introduce=introduce)
            messages.success(request, '科室已成功添加')
        return redirect('adminApp:keshi')
    return redirect('adminApp:keshi')

def delete_department(request):
    if request.method == 'POST':
        department_id = request.POST.get('department_id')
        department = get_object_or_404(Department, id=department_id)
        department.delete()
        messages.success(request, '科室已成功删除')
        return redirect('adminApp:keshi')
    return redirect('adminApp:keshi')


def info(request):

    userinfos = Userinfo.objects.all()
    pEinfos = PEinfo.objects.all()
    visits = Visit.objects.all()


    return render(request, 'info_manage.html', {'userinfos': userinfos,'pEinfos': pEinfos,'visits': visits})

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from django.contrib import messages
def ehi(request, infoid):
    userinfo = get_object_or_404(Userinfo, infoid=infoid)

    if request.method == 'POST':
        userinfo.user_name = request.POST.get('user_name')
        userinfo.user_height = request.POST.get('user_height')
        userinfo.user_weight = request.POST.get('user_weight')
        userinfo.allergy = request.POST.get('allergy')
        userinfo.illness = request.POST.get('illness')
        userinfo.disability = request.POST.get('disability')
        userinfo.common_drugs = request.POST.get('common_drugs')

        userinfo.save()
        messages.success(request, '健康档案已成功更新')
        return redirect(reverse('adminApp:info'))

    return render(request, 'ehi.html', {'userinfo': userinfo})
def ehi1(request, PEid):
    pEinfo = get_object_or_404(PEinfo, PEid=PEid)
    if request.method == 'POST':
        pEinfo.user_name = request.POST.get('user_name')
        pEinfo.user_sex = request.POST.get('user_sex')
        pEinfo.blood_sugar = request.POST.get('blood_sugar')
        pEinfo.total_cholesterol = request.POST.get('total_cholesterol')
        pEinfo.triglyceride = request.POST.get('triglyceride')
        pEinfo.minimum = request.POST.get('minimum')
        pEinfo.maximum = request.POST.get('maximum')
        pEinfo.heart_rate = request.POST.get('heart_rate')

        pEinfo.save()
        messages.success(request, '健康档案已成功更新')
        return redirect(reverse('adminApp:info'))

    return render(request, 'ehi1.html', {'pEinfo': pEinfo})

def ehi2(request, vid):
    visit = get_object_or_404(Visit, vid=vid)
    if request.method == 'POST':
        visit.user_name = request.POST.get('user_name')
        visit.user_sex = request.POST.get('user_sex')
        visit.department = request.POST.get('department')
        visit.chief_complaint = request.POST.get('chief_complaint')
        visit.HPI = request.POST.get('HPI')
        visit.PH = request.POST.get('PH')
        visit.diagnose = request.POST.get('diagnose')
        visit.DA = request.POST.get('DA')
        visit.prescription= request.POST.get('prescription')
        visit.save()
        messages.success(request, '健康档案已成功更新')
        return redirect(reverse('adminApp:info'))

    return render(request, 'ehi2.html', {'visit': visit})


@login_role_auth
def health_news(request):#健康咨询管理
    t=request.GET.get('t')
    news_id=request.GET.get('id')
    if request.method=="GET" and not t:
        news=News.objects.all()
        return render(request,"news_manage.html",{"news":news})
    elif request.method=="GET" and t=='show':
        news=News.objects.filter(news_id=news_id).first()
        return render(request,"news_details-manage.html",{"news":news})
    elif request.method=="GET" and t=='delete':
        news=News.objects.filter(news_id=news_id).first()
        news.delete()

        return redirect("/admin_sys/health_news/")

    elif request.method=="POST":
        type=request.POST.get("type")
        if type=="add":
            news=News()
            news.news_img=request.POST.get("news_img",'/static/img/news-1.jpg')
            news.news_content=request.POST.get("news_content")
            news.news_title=request.POST.get("news_title")
            news.save()
        elif type=="change":
            news_id=request.POST.get("news_id")
            news=News.objects.filter(news_id=news_id).first()
            news.news_img=request.POST.get("news_img",'/static/img/news-1.jpg')
            news.news_content=request.POST.get("news_content")
            news.news_title=request.POST.get("news_title")
            news.save()
        return redirect("/admin_sys/health_news/")
        
@login_role_auth
def blog_manage(request):#论坛管理
    pid=request.GET.get("pid")
    if request.method=="GET" and not pid:
        posts=Post.objects.all()
        return render(request,"discuss_manage.html",{"posts":posts})
    elif pid:
        type=request.GET.get("type")
        if type=="delete":
            post=Post.objects.filter(post_id=pid).first()
            post.delete()
            return redirect("/admin_sys/discuss_manage/")
        elif type=="show":
            post=Post.objects.filter(post_id=pid).first()
            # post.delete()
            comments=Comment.objects.filter(p_id=post)
            return render(request,"post-manage.html",{"post":post,'comments':comments})

@login_role_auth
def rights_manage(request):#权限管理 查 审核 删除 0申请1通过2不通过 
    if request.method=="GET":
        users=User.objects.all()
        doctors=Doctor.objects.all()
        return render(request,"blog_manage.html",{"users":users,'doctors':doctors})
    elif request.method=="POST":
        type=request.POST.get("type")
        if type=="agree":#通过
            pass
        elif type=="disagree":#不通过
            pass
        elif type=="delete":
            pass
    pass
