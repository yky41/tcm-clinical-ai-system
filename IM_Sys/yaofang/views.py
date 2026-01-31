
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator

from UserApp.models import User, Health_doc, Relative, Userinfo, PEinfo, Visit, CrawledContent
from django.http import HttpResponseRedirect
from DoctorApp.models import Doctor, Register, Department, Consult
from BlogApp.models import News, Post, Comment

from django.views.decorators.csrf import csrf_exempt
from py2neo import Graph, Node, Relationship
def login_role_auth(fn):
    def wrapper(request, *args, **kwargs):
        if request.session.get('is_login', False) and request.session.get('user_type') == "/user":
            return fn(request, *args, *kwargs)
        else:
            # 获取用户当前访问的url，并传递给/user/login/
            next = request.get_full_path()
            request.session["is_login"] = False
            red = HttpResponseRedirect("/login/?" + next)
            return red

    return wrapper


# Create your views here.
@login_role_auth
def change_pwd(request):  # 个人中心 修改密码
    massage = {"info": ''}
    if request.method == "POST":
        old_pwd = request.POST.get("old_pwd")
        new_pwd = request.POST.get("new_pwd")
        if old_pwd == new_pwd:
            massage = {"info": '新密码和原密码一致', "res": 0}
        else:
            user = User.objects.filter(uid=request.session.get('uid')).first()
            if user.password != old_pwd:
                massage = {"info": '原密码不正确', "res": 1}
            else:
                user.password = new_pwd
                user.save()
                massage = {"info": '密码修改成功', "res": 2}

    return JsonResponse(massage)


@login_role_auth
def personal_info(request):  # 个人中心 个人信息
    user = User.objects.filter(uid=request.session.get('uid')).first()
    infos = Userinfo.objects.filter(uid=user).order_by('-c_time')
    nui = infos.first()  # 最新个人信息

    return render(request, "user_index.html", {"user": user, 'nui': nui})


@login_role_auth
def user_basic(request):  # 个人中心 个人基本信息

    user = User.objects.filter(uid=request.session.get('uid')).first()
    return render(request, "user_basic.html", {"user": user})


@login_role_auth
def health_archives(request):  # 档案管理
    if request.method == "GET":
        health_doc = Health_doc.objects.filter(uid=request.session.get("uid"))
        return render(request, ".html", {"health_doc": health_doc})
    if request.method == "POST":
        pass


def personal_add(request):  # 个人档案添加
    user = User.objects.filter(uid=request.session.get('uid')).first()
    departments = Department.objects.all()  # 查询所有科室
    if request.method == "POST":
        type = request.POST.get("type")
        id = request.POST.get("id")
        if type == "info":
            ui = Userinfo.objects.filter(infoid=id).first() if id else Userinfo()
            # ui=Userinfo()

            ui.uid = user
            user_name = request.POST.get("user_name")
            user.user_name = user_name
            ui.user_name = user_name
            user_sex = request.POST.get("user_sex")
            user.user_sex = user_sex
            ui.user_sex = user_sex
            user_age = request.POST.get("user_age")
            user.user_age = user_age
            ui.user_age = user_age
            user_height = request.POST.get("user_height")
            ui.user_height = user_height
            user_weight = request.POST.get("user_weight")
            ui.user_weight = user_weight
            allergy = request.POST.get("allergy")
            ui.allergy = allergy

            illness = request.POST.get("illness")
            ui.illness = illness
            disability = request.POST.get("disability")
            ui.disability = disability

            common_drugs = request.POST.get("common_drugs")
            ui.common_drugs = common_drugs
            if not id:
                user.save()
            ui.save()

            return redirect("/user/personal_manage/")
        elif type == "PE":
            # p=PEinfo()
            p = PEinfo.objects.filter(PEid=id).first() if id else PEinfo()

            p.uid = user

            # user_name=request.POST.get("user_name")
            p.user_name = user.user_name

            # user_sex=request.POST.get("user_sex")
            p.user_sex = user.user_sex

            hospital = request.POST.get("hospital")
            p.hospital = hospital

            items = request.POST.get("items", '')
            p.items = items

            blood_sugar = request.POST.get("blood_sugar")
            p.blood_sugar = blood_sugar

            total_cholesterol = request.POST.get("total_cholesterol")
            p.total_cholesterol = total_cholesterol

            triglyceride = request.POST.get("triglyceride")
            p.triglyceride = triglyceride

            minimum = request.POST.get("minimum")
            p.minimum = minimum

            maximum = request.POST.get("maximum")
            p.maximum = maximum

            heart_rate = request.POST.get("heart_rate")
            p.heart_rate = heart_rate
            date = request.POST.get("date")
            p.date = date

            p.save()

            return redirect("/user/personal_manage/")

        elif type == "visit":
            # v=Visit()
            v = Visit.objects.filter(vid=id).first() if id else Visit()
            departments = Department.objects.all()  # 查询所有科室

            v.uid = user

            # user_name=request.POST.get("user_name")
            v.user_name = user.user_name

            # user_sex=user.request.POST.get("user_sex")
            v.user_sex = user.user_sex

            department = request.POST.get("department")
            v.department = department

            chief_complaint = request.POST.get("chief_complaint")
            v.chief_complaint = chief_complaint

            HPI = request.POST.get("HPI")
            v.HPI = HPI

            PH = request.POST.get("PH")
            v.PH = PH

            diagnose = request.POST.get("diagnose")
            v.diagnose = diagnose

            prescription = request.POST.get("prescription")
            v.prescription = prescription

            DA = request.POST.get("DA")
            v.DA = DA

            date = request.POST.get("date")
            v.date = date

            v.save()

            return redirect("/user/personal_manage/")

    return render(request, "personal_add.html",
                  {"user": user, 'active_menu': 'personal_add', 'departments': departments})


@login_role_auth
def personal_manage(request):  # 个人健康档案管理
    user = User.objects.filter(uid=request.session.get('uid')).first()
    if request.method == "GET":
        t = request.GET.get("type")
        i = request.GET.get("id")
        change = request.GET.get("change")
        if t and not change:
            if t == "info":
                info = Userinfo.objects.filter(infoid=i).first()
                info.delete()
            if t == "visit":
                v = Visit.objects.filter(vid=i).first()
                v.delete()
            if t == "PE":
                p = PEinfo.objects.filter(PEid=i).first()
                p.delete()
            return redirect("/user/personal_manage/")
        elif t and change:
            if t == "info":
                info = Userinfo.objects.filter(infoid=i).first()
                return render(request, "change_info.html", {"info": info, 'active_menu': 'personal_manage'})
            if t == "visit":
                v = Visit.objects.filter(vid=i).first()
                return render(request, "change_visit.html", {"v": v, 'active_menu': 'personal_manage'})
            if t == "PE":
                p = PEinfo.objects.filter(PEid=i).first()
                return render(request, "change_PE.html", {"p": p, 'active_menu': 'personal_manage'})
            pass

        infos = Userinfo.objects.filter(uid=user).order_by('-c_time')
        nui = infos.first()  # 最新个人信息
        PEs = PEinfo.objects.filter(uid=user).order_by('-c_time')  # 体检信息
        vs = Visit.objects.filter(uid=user).order_by('-c_time')  # 就诊记录

        return render(request, "personal_manage.html", {"user": user, "nui": nui, "infos": infos, 'PEs': PEs, "vs": vs,
                                                        'active_menu': 'personal_manage'})
    elif request.method == "POST":
        iid = request.POST.get("iid")
        if iid:
            ui = Userinfo.objects.filter(infoid=iid).first()
        else:
            ui = Userinfo()
        ui.uid = user
        user_name = request.POST.get("user_name")
        user.user_name = user_name
        ui.user_name = user_name
        user_sex = request.POST.get("user_sex")
        user.user_sex = user_sex
        ui.user_sex = user_sex
        user_age = request.POST.get("user_age")
        user.user_age = user_age
        ui.user_age = user_age
        user_height = request.POST.get("user_height")
        ui.user_height = user_height
        user_weight = request.POST.get("user_weight")
        ui.user_weight = user_weight
        allergy = request.POST.get("allergy")
        ui.allergy = allergy

        illness = request.POST.get("illness")
        ui.illness = illness
        disability = request.POST.get("disability")
        ui.disability = disability
        id_no = request.POST.get("id_no")
        phone = request.POST.get("phone")
        user.id_no = id_no
        user.phone = phone

        common_drugs = request.POST.get("common_drugs")
        ui.common_drugs = common_drugs

        ui.save()
        user.save()
        return redirect("/user/personal_manage/")


@login_role_auth
def family_add(request):  # 家庭健康档案添加
    if request.method == "POST":
        user = User.objects.filter(uid=request.session.get('uid')).first()
        relative = Relative()
        relative.uid = user
        relative.relationship = request.POST.get('relationship')
        relative.relative_name = request.POST.get('relative_name')
        relative.relative_sex = request.POST.get('relative_sex')
        relative.relative_age = request.POST.get('relative_age')
        relative.relative_height = request.POST.get('relative_height')
        relative.relative_weight = request.POST.get('relative_weight')
        relative.relative_allergy = request.POST.get('relative_allergy')
        relative.relative_illness = request.POST.get('relative_illness')
        relative.disability = request.POST.get('disability')
        relative.relative_surgery = request.POST.get('relative_surgery')
        relative.relative_injury = request.POST.get('relative_injury')
        relative.common_drugs = request.POST.get('common_drugs')
        relative.save()
        return redirect("/user/family_manage/")

    return render(request, "family_add.html", {'active_menu': 'family_add'})


@login_role_auth
def family_manage(request):  # 家庭健康档案管理
    if request.method == "GET":

        relatives = Relative.objects.filter(uid=request.session.get('uid'))
        # print(relatives)
        rid = request.GET.get('rid')
        # print(rid)
        if rid:
            relative = Relative.objects.filter(id=rid).first()
        else:
            relative = relatives.first() if relatives else None
        if request.GET.get('type'):
            relative.delete()
            return redirect(f"/user/family_manage/")

        return render(request, 'family_manage.html',
                      {'active_menu': 'family_manage', 'relatives': relatives, 'relative': relative,
                       'rid': relative.id if relative else None})
    elif request.method == "POST":
        rid = request.POST.get('rid')
        user = User.objects.filter(uid=request.session.get('uid')).first()

        if rid:
            relative = Relative.objects.filter(id=rid).first()
        else:
            relative = Relative()
            relative.uid = user
        relative.relative_name = request.POST.get('relative_name')
        relative.relative_sex = request.POST.get('relative_sex')
        relative.relative_age = request.POST.get('relative_age')
        relative.relative_height = request.POST.get('relative_height')
        relative.relative_weight = request.POST.get('relative_weight')
        relative.relative_allergy = request.POST.get('relative_allergy')
        relative.relative_illness = request.POST.get('relative_illness')
        relative.disability = request.POST.get('disability')
        relative.relative_surgery = request.POST.get('relative_surgery')
        relative.relative_injury = request.POST.get('relative_injury')
        relative.common_drugs = request.POST.get('common_drugs')
        relative.save()
        return redirect(f"/user/family_manage/?rid={relative.id}")


@login_role_auth
def online_consult(request):  # 线上咨询
    if request.method == "GET":
        did = request.GET.get("did")
        deid = request.GET.get("deid")
        if did:
            doctor = Doctor.objects.filter(uid=did).first()
            return render(request, "symptom.html", {"doctor": doctor})
        if deid:
            doctors = Doctor.objects.filter(deid=deid)
            de = Department.objects.filter(id=deid).first()
            # deid=request.GET.get("deid")
        else:
            doctors = Doctor.objects.all()
            de = []
        departments = Department.objects.all()
        # doctors=Doctor.objects.all()
        return render(request, "choose_doctor.html",
                      {"doctors": doctors, "departments": departments, 'de': de, 'active_menu': 'online_consult'})

        # return render(request,"online_consult.html",{"doctors":doctors,"departments":departments})
    elif request.method == "POST":
        did = request.POST.get("did")  # 医生编号
        target = request.POST.get("target")  # 目标
        howlong = request.POST.get("howlong")  # 持续时间
        drugs = request.POST.get("drugs")  # 药品
        con = Consult()
        print(did)
        con.d_id = Doctor.objects.filter(uid=did).first()
        print(request.session.get("uid"))
        con.u_id = User.objects.filter(uid=request.session.get("uid")).first()
        con.target = target
        con.howlong = howlong
        con.drugs = drugs
        con.state = 0
        con.save()
        return redirect("/user/my_online_consult/")


@login_role_auth
def my_online_consult(request):  # 我的线上咨询
    if request.method == "GET":
        cid = request.GET.get('cid')
        delete = request.GET.get('delete')
        if cid and not delete:
            c = Consult.objects.filter(c_id=cid).first()
            return render(request, "prescription_detail.html", {'c': c})
        elif cid and delete:
            c = Consult.objects.filter(c_id=cid).first()
            # print(1)
            c.delete()

            return redirect("/user/my_online_consult/")
        consults = Consult.objects.filter(u_id=User.objects.filter(uid=request.session.get("uid")).first())
        return render(request, "my_online_consult.html", {'consults': consults, "active_menu": 'my_online_consult'})


@login_role_auth
def register_online(request):  # 线上挂号
    if request.method == "GET":
        doctors = Doctor.objects.all().values()
        departments = Department.objects.all()
        rid = request.GET.get("rid")
        doc = []
        # print(doctors)
        for i in doctors:
            doc.append(
                {'uid': i["uid"], 'doctor_name': i["doctor_name"], 'title': i['title'], "department": i['deid_id'],
                 'hospital': i['hospital']})
        user = User.objects.filter(uid=request.session.get("uid")).first()
        if rid:
            r = Register.objects.filter(r_id=rid).first()
            return render(request, "register_online_change.html",
                          {"doctors": doc, "user": user, "departments": departments, 'r': r,
                           'active_menu': 'register_online'})
        time_range = ['8:00-8:30', '8:30-9:00', '9:00-9:30', '10:00-10:30', '10:30-11:00', '11:30-12:00', '14:00-14:30',
                      '14:30-15:00', '15:00-15:30', '15:30-16:00', '16:00-16:30', '16:30-17:00']
        return render(request, "register_online.html",
                      {"doctors": doc, "user": user, "departments": departments, 'active_menu': 'register_online',
                       'time_range': time_range})
    elif request.method == "POST":
        user_id = request.POST.get("uid")

        d_id = request.POST.get("d_id")
        # print(user_id,d_id)

        r_type = request.POST.get("r_type")
        date = request.POST.get("date")
        s_time = request.POST.get("s_time")
        change = request.POST.get("change")
        if change:
            re = Register.objects.filter(r_id=change).first()
        else:
            re = Register()
        re.d_id = Doctor.objects.filter(uid=d_id).first()

        re.u_id = User.objects.filter(uid=user_id).first()
        re.r_type = r_type
        re.date = date
        t_rang = s_time.split('-')
        re.s_time = t_rang[0]
        re.end_time = t_rang[1]
        re.save()
        return redirect("/user/user_register/")


def user_register(request):  # 我的预约
    if request.method == "GET":
        rid = request.GET.get('rid')
        if rid:
            r = Register.objects.filter(r_id=rid).first()
            r.delete()

            return redirect("/user/user_register/")
        my_re = Register.objects.filter(u_id=User.objects.filter(uid=request.session.get("uid")).first())

        return render(request, "user_register.html", {"my_re": my_re, 'active_menu': 'user_register'})
        # elif request.method=="POST":

    #     pass


# _________________________________________________________________________________________________________________
@login_role_auth
def news(request):
    # 指定要爬取的网页链接
    url = "http://www.xinhuanet.com/health/djk/index.html"

    # 在每次访问新闻页面时执行爬取操作
    scrape_and_save_to_database(url)

    p = request.GET.get('p', 1)
    size = request.GET.get("size", 5)
    q = request.GET.get('q')

    if request.method == "GET" and not q:
        page_obj = Paginator(CrawledContent.objects.all(), size)
        news = page_obj.get_page(p)
        return render(request, "news.html", {"news": news, 'active_menu': 'news'})

    elif request.method == "GET" and q:
        page_obj = Paginator(CrawledContent.objects.filter(title__contains=q), size)
        news = page_obj.get_page(p)
        return render(request, "news.html", {"news": news, 'active_menu': 'news', 'q': q})


import requests
from bs4 import BeautifulSoup

from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db import IntegrityError

from .models import CrawledContent  # 导入模型


def scrape_and_save_to_database(url):
    # 发送请求获取网页内容
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # 查找所有包含标题和链接的标签
    for item in soup.find_all("a", href=True, target="_blank"):
        title = item.text.strip()  # 获取标题文本
        link = item["href"]  # 获取链接地址

        # 创建 CrawledContent 模型对象并保存到数据库中
        try:
            CrawledContent.objects.create(title=title, link=link)
        except IntegrityError:
            # 如果已存在相同链接的内容，忽略并继续下一个
            pass


def news_details(request):
    n_id = request.GET.get("nid")
    if request.method == "GET" and n_id:
        news = CrawledContent.objects.filter(id=n_id).first()
        return render(request, "news_details.html", {"news": news})
    else:
        return redirect("/error/")


# ______________________________________________________________________________________________________
@login_role_auth
def blog(request):  # 论坛 增删查改
    q = request.GET.get('q')
    if request.method == "GET" and not q:
        page = request.GET.get("page", 1)
        user = User.objects.filter(uid=request.session.get("uid")).first()
        posts = Post.objects.all()
        return render(request, "discuss.html", {"posts": posts, 'user': user})
    elif request.method == "GET" and q:
        user = User.objects.filter(uid=request.session.get("uid")).first()
        posts = Post.objects.filter(post_title__contains=q)
        return render(request, "discuss.html", {"posts": posts, 'user': user, 'q': q})
    elif request.method == "POST":
        type = request.POST.get("type")
        if type == "add":
            title = request.POST.get("title", "")
            content = request.POST.get("content", "")
            post_type = request.POST.get("post_type", "")
            p = Post()
            p.post_title = title
            p.post_content = content
            p.post_type = post_type
            p.u_id = User.objects.filter(uid=request.session.get("uid")).first()
            p.save()
            return redirect("/user/blog/")  # JsonResponse({"status":"200","info":"ok"})
        elif type == "delete":
            p_id = request.POST.get("pid", None)
            p = Post.objects.filter(post_id=p_id).first()
            if p.u_id == User.objects.filter(uid=request.session.get("uid")).first():
                p.delete()
            else:
                return JsonResponse({"state": 400, "info": "error"})
            return JsonResponse({"state": 200, "info": "ok"})

            # return redirect("/user/blog/")#JsonResponse({"status":"200","info":"ok"})
        elif type == "change":
            p_id = request.POST.get("pid", None)
            title = request.POST.get("title", "")
            content = request.POST.get("content", "")
            post_type = request.POST.get("post_type", "")
            p = Post.objects.filter(p_id).first()
            p.post_title = title
            p.post_content = content
            p.post_type = post_type
            p.save()
            return JsonResponse({"state": 200, "info": "ok"})


@login_role_auth
def like_post(request):  # 点赞/取消点赞帖子
    try:
        user = User.objects.filter(uid=request.session.get("uid")).first()
        pid = request.POST.get('pid')
        p = Post.objects.filter(post_id=pid).first()
        if p:
            user_like = p.users_like.filter(uid=user.uid).first()
            # 查询当前用户是否为当前文章点过赞
            type = 1
            if user_like:
                # 点赞过
                type = 0
                p.users_like.remove(user)
            else:
                # 没点赞
                p.users_like.add(user)
            like_sum = p.users_like.count()
            return JsonResponse({'state': 200, 'type': type, 'like_sum': like_sum})
        else:
            return JsonResponse({'state': 400, 'data': '点赞无效'})
    except Exception as e:
        return JsonResponse({'state': 500, 'data': f'出现异常：{e}'})


@login_role_auth
def blog_details(request):  # 博客详情
    p_id = request.GET.get("pid", None)
    if request.method == "GET" and p_id:

        post = Post.objects.filter(post_id=p_id).first()
        comments = Comment.objects.filter(p_id=post)
        return render(request, "post.html", {"post": post, 'comments': comments})
    else:
        return redirect("/error/")


@login_role_auth
def comment(request):  # 评论
    post_id = request.GET.get("pid")
    if request.method == "GET" and post_id:
        comments = Comment.objects.filter(p_id=post_id)
        return render(request, "comments.html", {"comments": comments})
    elif request.method == "POST":
        comment = Comment()
        content = request.POST.get("content", "")
        comment.content = content
        p_id = request.POST.get("pid", None)
        p = Post.objects.filter(post_id=p_id).first()
        comment.p_id = p
        comment.u_id = User.objects.filter(uid=request.session.get("uid")).first()
        comment.save()
        return redirect("/user/blog/")  # JsonResponse({"status":"200","info":"ok"})


from UserApp.QA.qa import KBQA1
from UserApp.QA.jian import PrescriptionSaver

current_question_index = 0
current_question_index1 = 0
is_prescription_query = False
additional_prescription_query = False
new_prescription_step = None
new_prescription = {'方名': '', '主治': '', '组成': '', '方剂类型': '', '用法': ''}
user_answers = []


# 初始化状态
def reset_state():
    global current_question_index
    global is_prescription_query
    global user_answers
    global current_question_index1
    global additional_prescription_query
    global new_prescription_step
    global new_prescription

    current_question_index = 0
    current_question_index1 = 0
    is_prescription_query = False
    additional_prescription_query = False
    new_prescription_step = None
    new_prescription = {'方名': '', '主治': '', '组成': '', '方剂类型': '', '用法': ''}
    user_answers = []


class PrescriptionSaver:
    def __init__(self, uri, user, password):
        self.graph = Graph(uri, auth=(user, password))

    def save_prescription(self, prescription):
        try:
            prescription_type = prescription["方剂类型"]
            prescription_name = prescription["方名"]
            composition = prescription["组成"]
            indications = prescription["主治"]
            usage = prescription["用法"]

            prescription_type_node = self.graph.nodes.match("方剂类型", name=prescription_type).first()
            if not prescription_type_node:
                prescription_type_node = Node("方剂类型", name=prescription_type)
                self.graph.create(prescription_type_node)

            prescription_node = self.graph.nodes.match("方名", name=prescription_name).first()
            if not prescription_node:
                prescription_node = Node('方名', name=prescription_name, 方剂类型=prescription_type)
                self.graph.create(prescription_node)

            composition_node = self.graph.nodes.match("组成", name=composition).first()
            if not composition_node:
                composition_node = Node("组成", name=composition)
                self.graph.create(composition_node)

            indications_node = self.graph.nodes.match("主治", name=indications).first()
            if not indications_node:
                indications_node = Node("主治", name=indications)
                self.graph.create(indications_node)

            usage_node = self.graph.nodes.match("用法", name=usage).first()
            if not usage_node:
                usage_node = Node("用法", name=usage)
                self.graph.create(usage_node)

            prescription_node["方剂类型"] = prescription_type
            self.graph.push(prescription_node)

            relation1 = Relationship(prescription_node, "组成", composition_node)
            relation2 = Relationship(prescription_node, "主治", indications_node)
            relation3 = Relationship(prescription_node, "用法", usage_node)
            relation4 = Relationship(prescription_node, "方剂类型", prescription_type_node)

            self.graph.merge(relation1)
            self.graph.merge(relation2)
            self.graph.merge(relation3)
            self.graph.merge(relation4)

            print(f"Prescription {prescription_name} saved successfully.")
        except Exception as e:
            print(f"Error saving prescription: {e}")

def add_prescription(request):
    return render(request, "add_prescription.html")

@csrf_exempt
def save_prescription(request):
    if request.method == "POST":
        name = request.POST.get("name")
        prescription_type = request.POST.get("type")
        composition = request.POST.get("composition")
        usage = request.POST.get("usage")
        indications = request.POST.get("indications")

        # 保存新药方的逻辑
        new_prescription = {
            "方名": name,
            "方剂类型": prescription_type,
            "组成": composition,
            "用法": usage,
            "主治": indications
        }
        saver = PrescriptionSaver("bolt://localhost:7687", "neo4j", "12345678")
        saver.save_prescription(new_prescription)

        return redirect("UserApp:answer")  # 保存成功后重定向回主页面

    return render(request, "add_prescription.html")

class PrescriptionSaver:
    def __init__(self, uri, user, password):
        self.graph = Graph(uri, auth=(user, password))

    def save_prescription(self, prescription):
        try:
            prescription_type = prescription["方剂类型"]
            prescription_name = prescription["方名"]
            composition = prescription["组成"]
            indications = prescription["主治"]
            usage = prescription.get("用法", "")

            prescription_type_node = self.graph.nodes.match("方剂类型", name=prescription_type).first()
            if not prescription_type_node:
                prescription_type_node = Node("方剂类型", name=prescription_type)
                self.graph.create(prescription_type_node)

            prescription_node = self.graph.nodes.match("方名", name=prescription_name).first()
            if not prescription_node:
                prescription_node = Node('方名', name=prescription_name, 方剂类型=prescription_type)
                self.graph.create(prescription_node)

            composition_node = self.graph.nodes.match("组成", name=composition).first()
            if not composition_node:
                composition_node = Node("组成", name=composition)
                self.graph.create(composition_node)

            indications_node = self.graph.nodes.match("主治", name=indications).first()
            if not indications_node:
                indications_node = Node("主治", name=indications)
                self.graph.create(indications_node)

            usage_node = self.graph.nodes.match("用法", name=usage).first()
            if not usage_node:
                usage_node = Node("用法", name=usage)
                self.graph.create(usage_node)

            rel = Relationship(prescription_type_node, "包含", prescription_node)
            self.graph.create(rel)
            rel = Relationship(prescription_node, "组成部分", composition_node)
            self.graph.create(rel)
            rel = Relationship(prescription_node, "主治", indications_node)
            self.graph.create(rel)
            rel = Relationship(prescription_node, "用法", usage_node)
            self.graph.create(rel)

            return True
        except Exception as e:
            print(e)
            return False
def answer(request):
    global current_question_index
    global is_prescription_query
    global user_answers
    global current_question_index1
    global additional_prescription_query
    global new_prescription_step
    global new_prescription

    first_series_questions = [
        "请问您有什么不适的症状？",
        "还有什么症状？",
        "还有呢?"
    ]

    second_series_questions = [
        "发烧吗？",
        "是否有喉咙痛的症状？",
        "有痰吗",
        "嗓子红吗",
        "流鼻涕吗",
        "咳嗽吗？"
    ]

    if request.method == "POST":
        question = request.POST.get('msg').strip()
        try:
            answer = ''
            additional_question = ''

            if "刷新" in question:
                reset_state()
                return JsonResponse({'answer': "已重置会话状态，请重新开始。"})

            if question:
                if "2" in question:  # 查药方
                    answer = "请输入药材或症状："
                    is_prescription_query = True
                    additional_prescription_query = False
                elif "1" in question:  # 问诊
                    is_prescription_query = False
                    additional_prescription_query = False

                    if "感冒" in user_answers:  # 检查用户是否输入了感冒
                        if current_question_index1 < len(second_series_questions):  # 提问第二系列问题
                            answer = second_series_questions[current_question_index1]
                            current_question_index1 += 1
                        else:
                            matched_prescriptions = KBQA1.filter_prescription_by_indications(user_answers)
                            if matched_prescriptions:
                                prescriptions_info = ""
                                for prescription in matched_prescriptions:
                                    prescription_info = f"药方: {prescription['药方']}<br>主治: {prescription['主治']}<br>方剂类型: {prescription['方剂类型']}<br>用法: {prescription['用法']}<br>组成: {prescription['组成']}<br>匹配病症: {prescription['匹配病症']}"
                                    prescriptions_info += f"根据您的回答，建议您尝试药方：<br>{prescription_info}<br><br>"
                                answer = prescriptions_info
                                additional_question = "是否需要补充药材？"
                                additional_prescription_query = True
                            else:
                                answer = "很抱歉，没有找到匹配的药方。"
                    else:
                        if current_question_index < len(first_series_questions):
                            answer = first_series_questions[current_question_index]
                            current_question_index += 1
                        else:
                            user_answers.append(question)
                            matched_prescriptions = KBQA1.filter_prescription_by_indications(user_answers)
                            if matched_prescriptions:
                                prescriptions_info = ""
                                for prescription in matched_prescriptions:
                                    prescription_info = f"药方: {prescription['药方']}<br>主治: {prescription['主治']}<br>方剂类型: {prescription['方剂类型']}<br>用法: {prescription['用法']}<br>组成: {prescription['组成']}<br>匹配病症: {prescription['匹配病症']}"
                                    prescriptions_info += f"根据您的回答，建议您尝试药方：<br>{prescription_info}<br><br>"
                                answer = prescriptions_info
                                additional_question = "是否需要补充药材？"
                                additional_prescription_query = True
                            else:
                                answer = "很抱歉，没有找到匹配的药方。"
                elif is_prescription_query:  # 查药方
                    answer = KBQA1.match_cure_for_condition(question)
                    if not answer:
                        prescription_info = KBQA1.match_cure_for_condition1(question)
                        if prescription_info:
                            answer = f"根据您的回答，建议您尝试药方：<br>{prescription_info}"
                            additional_question = "是否需要补充药材？"
                            additional_prescription_query = True
                        else:
                            answer = "很抱歉，没有找到匹配的药方。"
                    is_prescription_query = True
                elif additional_prescription_query:
                    if question.lower() in ["是", "yes"]:
                        answer = "请输入药材或症状："
                        is_prescription_query = True
                        additional_prescription_query = False
                    elif question.lower() in ["否", "no"]:
                        answer = "请输入药方信息，包括'方名', '主治', '组成', '方剂类型', '用法'。"
                        additional_prescription_query = False
                        new_prescription_step = '方名'
                elif new_prescription_step:
                    if new_prescription_step == '方名':
                        new_prescription['方名'] = question
                        answer = "请输入方剂类型："
                        new_prescription_step = '方剂类型'
                    elif new_prescription_step == '方剂类型':
                        new_prescription['方剂类型'] = question
                        answer = "请输入组成："
                        new_prescription_step = '组成'
                    elif new_prescription_step == '组成':
                        new_prescription['组成'] = question
                        answer = "请输入主治："
                        new_prescription_step = '主治'
                    elif new_prescription_step == '主治':
                        new_prescription['主治'] = question
                        answer = "请输入用法："
                        new_prescription_step = '用法'
                    elif new_prescription_step == '用法':
                        new_prescription['用法'] = question
                        # 保存新药方的逻辑
                        saver = PrescriptionSaver("bolt://localhost:7687", "neo4j", "12345678")
                        saver.save_prescription(new_prescription)
                        answer = "新药方已保存成功。"
                        reset_state()
                else:
                    user_answers.append(question)
                    if "感冒" in user_answers:
                        if current_question_index1 < len(second_series_questions):
                            answer = second_series_questions[current_question_index1]
                            current_question_index1 += 1
                        else:
                            matched_prescriptions = KBQA1.filter_prescription_by_indications(user_answers)
                            if matched_prescriptions:
                                prescriptions_info = ""
                                for prescription in matched_prescriptions:
                                    prescription_info = f"药方: {prescription['药方']}<br>主治: {prescription['主治']}<br>方剂类型: {prescription['方剂类型']}<br>用法: {prescription['用法']}<br>组成: {prescription['组成']}<br>匹配病症: {prescription['匹配病症']}"
                                    prescriptions_info += f"根据您的回答，建议您尝试药方：<br>{prescription_info}<br><br>"
                                answer = prescriptions_info
                                additional_question = "是否需要补充药材？"
                                additional_prescription_query = True
                            else:
                                answer = "很抱歉，没有找到匹配的药方。"
                    else:
                        if current_question_index < len(first_series_questions):
                            answer = first_series_questions[current_question_index]
                            current_question_index += 1
                        else:
                            matched_prescriptions = KBQA1.filter_prescription_by_indications(user_answers)
                            if matched_prescriptions:
                                prescriptions_info = ""
                                for prescription in matched_prescriptions:
                                    prescription_info = f"药方: {prescription['药方']}<br>主治: {prescription['主治']}<br>方剂类型: {prescription['方剂类型']}<br>用法: {prescription['用法']}<br>组成: {prescription['组成']}<br>匹配病症: {prescription['匹配病症']}"
                                    prescriptions_info += f"根据您的回答，建议您尝试药方：<br>{prescription_info}<br><br>"
                                answer = prescriptions_info
                                additional_question = "是否需要补充药材？"
                                additional_prescription_query = True
                            else:
                                answer = "很抱歉，没有找到匹配的药方。"
        except Exception as e:
            print(e)
            answer = "对不起，您的问题我不知道，我今后会努力改进的。"
        return JsonResponse({'answer': answer, 'additional_question': additional_question})
    return render(request, "answer.html", {'active_menu': 'answer'})







