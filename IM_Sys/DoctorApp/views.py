
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator

from UserApp.models import User, Health_doc, Relative, Userinfo, PEinfo, Visit, CrawledContent
from django.http import HttpResponseRedirect
from DoctorApp.models import Doctor, Register, Department, Consult,Recipe
from BlogApp.models import News, Post, Comment
import json
from django.views.decorators.csrf import csrf_exempt
from py2neo import Graph, Node, Relationship
# from django.http import HttpResponse,JsonResponse

from django.http import HttpResponseRedirect,JsonResponse
def login_role_auth(fn):
    def wrapper(request,*args,**kwargs):
        if request.session.get('is_login', False) and request.session.get('user_type')=="/doctor" :
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
            user=Doctor.objects.filter(uid=request.session.get('uid')).first()
            if user.password!=old_pwd:
                massage={"info":'原密码不正确',"res":1}
            else:
                user.password=new_pwd
                user.save()
                massage={"info":'密码修改成功',"res":2}
        return JsonResponse(massage) 
    else:
        return render(request,"doctor_passwd.html",massage)
def personal_info(request):#个人中心 个人信息
    if request.method=="GET":
        departments=Department.objects.all()
        doctor=Doctor.objects.filter(uid=request.session.get('uid')).first()
        return render(request,"doctor_index.html",{"user":doctor,'departments':departments})
    elif request.method=="POST":
        doctor_name=request.POST.get('doctor_name')
        uid=request.session.get('uid')
        email=request.POST.get('email')
        doctor_sex=request.POST.get('doctor_sex')
        doctor_age=request.POST.get('doctor_age')
        title=request.POST.get('title')
        hospital=request.POST.get('hospital')
        profile=request.POST.get('profile1')
        # role=request.POST.get('role')
        deid=request.POST.get('deid')
        good_at=request.POST.get('good_at')
        d=Doctor.objects.filter(uid=uid).first()
        d.doctor_name=doctor_name
        d.email=email
        d.doctor_sex=doctor_sex
        d.doctor_age=doctor_age
        d.title=title
        d.deid=Department.objects.filter(id=deid).first()
        d.hospital=hospital
        # d.role=role
        if profile:

            d.profile=profile
        d.good_at=good_at
        d.save()
        return redirect("/doctor/index/")
        

def online_consult(request):#线上咨询
    cid=request.GET.get('cid')
    type=request.GET.get('type')
    if request.method=="GET" and not cid:
        consults=Consult.objects.filter(d_id=request.session.get("uid"))
        return render(request,"online_manage.html",{'consults':consults})
    if request.method=="GET" and  cid and not type:
        # print(1)
        consult=Consult.objects.filter(c_id=cid).first()
        userinfo=Userinfo.objects.filter(uid=consult.u_id).first()
        return render(request,"treat_patient.html",{'consult':consult,'userinfo':userinfo})
    if request.method=="GET" and  cid and  type=="show":
        c=Consult.objects.filter(c_id=cid).first()
        return render(request,"consult_detail.html",{'c':c})
        # return render(request,"treat_patient.html",{'consult':consult,'userinfo':userinfo})
    if request.method=="POST":
        cid=request.POST.get('cid')
        consult=Consult.objects.filter(c_id=cid).first()
        diagnosisResult=request.POST.get('diagnosisResult')#诊断结果
        RP=request.POST.get('RP')#RP
        rp=Recipe()
        rp.Rp=RP
        rp.diagnose=diagnosisResult
        rp.symptom=''
        rp.save()
        consult.r_id=rp
        consult.status=1
        consult.save()
        return redirect("/doctor/online_consult/")

def register(request):#挂号/预约管理
    rid=request.GET.get('rid')
    if request.method=="GET" and not rid:
        registers=Register.objects.filter(d_id=request.session.get("uid"))
        return render(request,"register_manage.html",{'registers':registers})
    else:
        status=request.GET.get('status')
        register=Register.objects.filter(r_id=rid).first()
        register.status=status
        register.save()

        return redirect('/doctor/register/')


from DoctorApp.QA.qa1 import KBQA2
from DoctorApp.QA.jian import PrescriptionSaver

current_question_index = 0
current_question_index1 = 0
is_prescription_query = False
additional_prescription_query = False
new_prescription_step = None
new_prescription = {'方名': '', '主治': '', '组成': '', '方剂类型': '', '用法': ''}
user_answers = []

# Function to reset state
def reset_state():
    global current_question_index, is_prescription_query, user_answers, current_question_index1, additional_prescription_query, new_prescription_step, new_prescription
    current_question_index = 0
    current_question_index1 = 0
    is_prescription_query = False
    additional_prescription_query = False
    new_prescription_step = None
    new_prescription = {'方名': '', '主治': '', '组成': '', '方剂类型': '', '用法': ''}
    user_answers = []

# Class to save prescription to database
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

            rel = Relationship(prescription_type_node, "包含", prescription_node)
            self.graph.create(rel)
            rel = Relationship(prescription_node, "组成部分", composition_node)
            self.graph.create(rel)
            rel = Relationship(prescription_node, "主治", indications_node)
            self.graph.create(rel)
            rel = Relationship(prescription_node, "用法", usage_node)
            self.graph.create(rel)

            print(f"Prescription {prescription_name} saved successfully.")
        except Exception as e:
            print(f"Error saving prescription: {e}")

def add_prescription(request):
    # 从会话数据中获取药方列表（示例数据，这里应该从实际数据源获取）
    prescriptions = [
        {
            "药方": "六味汤",
            "方剂类型": "解表剂",
            "组成": "附子（炮）2两，细辛2两，甘草（炙）2两，人参2两，干姜3两，大黄5两。",
            "用法": "【用法用量】 上切。以水7升，煮取2升合，去滓，分温3服。服如人行10里久。1服此汤，当得快利，利中有恶物如鱼脑状，或如桃李，但异于常利，勿怪之。将息经3-4日，宜合高良姜等10味散服之。",
            "主治": "风寒喉痹，咽喉淡红不肿，吞咽不顺，恶寒发热，鼻流清涕",
            "匹配病症": "发热, 喉痹, 咽喉淡红不肿, 鼻流"
        },
        {
            "药方": "三拗汤",
            "方剂类型": "解表剂",
            "组成": "麻黄 杏仁 甘草",
            "用法": "nan",
            "主治": "感冒风邪，鼻塞声重，咳嗽痰多，胸闷气短",
            "匹配病症": "感冒, 痰, 咳嗽"
        },
        # 添加其他药方...
    ]

    prescriptions_json = json.dumps(prescriptions)
    return render(request, "add_prescription.html", {"prescriptions": prescriptions, "prescriptions_json": prescriptions_json})

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

        return redirect("DoctorApp:answer1")  # 保存成功后重定向回主页面

    return render(request, "add_prescription.html")

def answer1(request):
    global current_question_index, is_prescription_query, user_answers, current_question_index1, additional_prescription_query, new_prescription_step, new_prescription

    first_series_questions = [
        "请问您有什么不适的症状？",
        "还有什么症状？",
        "还有呢?"
    ]

    second_series_questions = [
        "发烧吗？",
        "是否有喉咙痛的症状？",
        "有痰吗？",
        "嗓子红吗？",
        "流鼻涕吗？",
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
                            matched_prescriptions = KBQA2.filter_prescription_by_indications(user_answers)
                            if matched_prescriptions:
                                prescriptions_info = ""
                                seen_prescriptions = set()
                                for prescription in matched_prescriptions:
                                    if prescription['药方'] not in seen_prescriptions:
                                        seen_prescriptions.add(prescription['药方'])
                                        prescription_info = (
                                            f"药方: {prescription['药方']}<br>"
                                            f"主治: {prescription['主治']}<br>"
                                            f"方剂类型: {prescription['方剂类型']}<br>"
                                            f"用法: {prescription['用法']}<br>"
                                            f"组成: {prescription['组成']}<br>"
                                            f"匹配病症: {prescription['匹配病症']}<br><br>"
                                        )
                                        prescriptions_info += prescription_info
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
                            if question not in ["不", "无"]:
                                user_answers.append(question)
                            matched_prescriptions = KBQA2.filter_prescription_by_indications(user_answers)
                            if matched_prescriptions:
                                prescriptions_info = ""
                                seen_prescriptions = set()
                                for prescription in matched_prescriptions:
                                    if prescription['药方'] not in seen_prescriptions:
                                        seen_prescriptions.add(prescription['药方'])
                                        prescription_info = (
                                            f"药方: {prescription['药方']}<br>"
                                            f"主治: {prescription['主治']}<br>"
                                            f"方剂类型: {prescription['方剂类型']}<br>"
                                            f"用法: {prescription['用法']}<br>"
                                            f"组成: {prescription['组成']}<br>"
                                            f"匹配病症: {prescription['匹配病症']}<br><br>"
                                        )
                                        prescriptions_info += prescription_info
                                answer = prescriptions_info
                                additional_question = "是否需要补充药材？"
                                additional_prescription_query = True
                            else:
                                answer = "很抱歉，没有找到匹配的药方。"
                elif is_prescription_query:  # 查药方
                    answer = KBQA2.match_cure_for_condition(question)
                    if not answer:
                        prescription_info = KBQA2.match_cure_for_condition1(question)
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
                        if new_prescription_step is None:
                            answer = "是否创建新药方？"
                            additional_prescription_query = False
                            new_prescription_step = '是否创建新药方'
                        else:
                            additional_prescription_query = False
                            answer = "问诊结束。"
                            reset_state()
                elif new_prescription_step:
                    if new_prescription_step == '是否创建新药方':
                        if question.lower() in ["是", "yes"]:
                            answer = "请输入新药方名："
                            new_prescription_step = '方名'
                            new_prescription = {}
                        elif question.lower() in ["否", "no"]:
                            answer = "问诊结束。"
                            reset_state()
                    elif new_prescription_step == '方名':
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
                    if question not in ["不", "无"]:
                        user_answers.append(question)
                    if "感冒" in user_answers:
                        if current_question_index1 < len(second_series_questions):
                            answer = second_series_questions[current_question_index1]
                            current_question_index1 += 1
                        else:
                            matched_prescriptions = KBQA2.filter_prescription_by_indications(user_answers)
                            if matched_prescriptions:
                                prescriptions_info = ""
                                seen_prescriptions = set()
                                for prescription in matched_prescriptions:
                                    if prescription['药方'] not in seen_prescriptions:
                                        seen_prescriptions.add(prescription['药方'])
                                        prescription_info = (
                                            f"药方: {prescription['药方']}<br>"
                                            f"主治: {prescription['主治']}<br>"
                                            f"方剂类型: {prescription['方剂类型']}<br>"
                                            f"用法: {prescription['用法']}<br>"
                                            f"组成: {prescription['组成']}<br>"
                                            f"匹配病症: {prescription['匹配病症']}<br><br>"
                                        )
                                        prescriptions_info += prescription_info
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
                            matched_prescriptions = KBQA2.filter_prescription_by_indications(user_answers)
                            if matched_prescriptions:
                                prescriptions_info = ""
                                seen_prescriptions = set()
                                for prescription in matched_prescriptions:
                                    if prescription['药方'] not in seen_prescriptions:
                                        seen_prescriptions.add(prescription['药方'])
                                        prescription_info = (
                                            f"药方: {prescription['药方']}<br>"
                                            f"主治: {prescription['主治']}<br>"
                                            f"方剂类型: {prescription['方剂类型']}<br>"
                                            f"用法: {prescription['用法']}<br>"
                                            f"组成: {prescription['组成']}<br>"
                                            f"匹配病症: {prescription['匹配病症']}<br><br>"
                                        )
                                        prescriptions_info += prescription_info
                                answer = prescriptions_info
                                additional_question = "是否需要补充药材？"
                                additional_prescription_query = True
                            else:
                                answer = "很抱歉，没有找到匹配的药方。"
        except Exception as e:
            print(e)
            answer = "对不起，您的问题我不知道，我今后会努力改进的。"
        return JsonResponse({'answer': answer, 'additional_question': additional_question})
    return render(request, "answer1.html", {'active_menu': 'answer'})




from DoctorApp.GNN import KBQA4
current_question_indexx = 0
current_question_indexx1 = 0
is_prescription_queryy = False
user_answerss = []

@csrf_exempt
def answer2(request):
    global current_question_indexx
    global is_prescription_queryy
    global user_answerss
    global current_question_indexx1

    # 一系列问题列表
    first_series_questions = [
        "请问您有什么不适的症状？",
        "还有什么症状？",
        "还有呢?"
        # 可以继续添加更多问题
    ]

    # 第二系列问题列表
    second_series_questions = [

        "是否有喉咙痛的症状？",
        "有痰吗？",
        "嗓子红吗？",

        # 可以继续添加更多问题
    ]

    if request.method == "POST":
        question = request.POST.get('msg')
        try:
            answer = ''
            print(question)
            print(user_answerss)
            if question:
                if "2" in question:  # 查药方
                    answer = "请输入药方："
                    is_prescription_query = True
                elif "1" in question:  # 问诊
                    is_prescription_query = False

                    if "感冒" in user_answerss:  # 检查用户是否输入了感冒
                        if current_question_indexx1 < len(second_series_questions):  # 提问第二系列问题
                            answer = second_series_questions[current_question_indexx1]
                            current_question_indexx1 += 1
                        else:
                            # 匹配药方
                            kbqa4 = KBQA4()
                            matched_prescription = kbqa4.get_prescriptions(user_answerss)
                            if matched_prescription:
                                prescription_info = f"药方: {matched_prescription['药方']}<br>匹配度: {matched_prescription['匹配度']}<br>主治: {matched_prescription['主治']}<br>方剂类型: {matched_prescription['方剂类型']}<br>用法: {matched_prescription['用法']}<br>组成: {matched_prescription['组成']}"
                                answer = f"根据您的回答，建议您尝试药方：<br>{prescription_info}"
                            else:
                                answer = "很抱歉，没有找到匹配的药方。"
                    else:
                        # 提问第一系列问题
                        if current_question_indexx < len(first_series_questions):
                            answer = first_series_questions[current_question_indexx]
                            current_question_indexx += 1
                        else:
                            # 记录用户的所有回答并匹配药方
                            user_answerss.append(question)
                            kbqa4 = KBQA4()
                            matched_prescription = kbqa4.get_prescriptions(user_answerss)
                            if matched_prescription:
                                prescription_info = f"药方: {matched_prescription['药方']}<br>匹配度: {matched_prescription['匹配度']}<br>主治: {matched_prescription['主治']}<br>方剂类型: {matched_prescription['方剂类型']}<br>用法: {matched_prescription['用法']}<br>组成: {matched_prescription['组成']}"
                                answer = f"根据您的回答，建议您尝试药方：<br>{prescription_info}"
                            else:
                                answer = "很抱歉，没有找到匹配的药方。"
                elif is_prescription_queryy:  # 查药方
                    kbqa4 = KBQA4()
                    answer = kbqa4.match_cure_for_condition(question)
                    # 在输出药方的结果后，添加新的提示
                    if not answer:
                        prescription_info = kbqa4.match_cure_for_condition1(question)
                        if prescription_info:
                            answer = f"根据您的回答，建议您尝试药方：<br>{prescription_info}"
                        else:
                            answer = "很抱歉，没有找到匹配的药方。"
                    is_prescription_query = True
                else:  # 问诊
                    user_answerss.append(question)
                    print(user_answerss)
                    if "感冒" in user_answerss:  # 检查用户是否输入了感冒
                        if current_question_indexx1 < len(second_series_questions):  # 提问第二系列问题
                            answer = second_series_questions[current_question_indexx1]
                            current_question_indexx1 += 1
                        else:
                            # 匹配药方
                            kbqa4 = KBQA4()
                            matched_prescription = kbqa4.get_prescriptions(user_answerss)
                            if matched_prescription:
                                prescription_info = f"药方: {matched_prescription['药方']}<br>匹配度: {matched_prescription['匹配度']}<br>主治: {matched_prescription['主治']}<br>方剂类型: {matched_prescription['方剂类型']}<br>用法: {matched_prescription['用法']}<br>组成: {matched_prescription['组成']}"
                                answer = f"根据您的回答，建议您尝试药方：<br>{prescription_info}"
                            else:
                                answer = "很抱歉，没有找到匹配的药方1。"
                    else:
                        # 继续提问第一系列问题
                        if current_question_indexx < len(first_series_questions):
                            answer = first_series_questions[current_question_indexx]
                            current_question_indexx += 1
                        else:
                            # 记录用户的所有回答并匹配药方
                            kbqa4 = KBQA4()
                            matched_prescription = kbqa4.get_prescriptions(user_answerss)
                            if matched_prescription:
                                prescription_info = f"药方: {matched_prescription['药方']}<br>匹配度: {matched_prescription['匹配度']}<br>主治: {matched_prescription['主治']}<br>方剂类型: {matched_prescription['方剂类型']}<br>用法: {matched_prescription['用法']}<br>组成: {matched_prescription['组成']}"
                                answer = f"根据您的回答，建议您尝试药方：<br>{prescription_info}"
                            else:
                                answer = "很抱歉，没有找到匹配的药方2。"
        except Exception as e:
            print(e)
            answer = "对不起，您的问题我不知道，我今后会努力改进的。"
        return JsonResponse({'answer': answer})
    return render(request, "ask_medicine.html", {'active_menu': 'answer'})