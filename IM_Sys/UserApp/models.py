import django
from django.db import models
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "IM_Sys.IM_Sys.settings")

# Create your models here.


class User(models.Model):#各种数据库的表
    uid = models.AutoField(primary_key=True)  # 用户编号
    user_name = models.CharField(max_length=20)  # 用户名
    email = models.CharField(max_length=20)  # 邮箱
    password = models.CharField(max_length=20)  # 密码
    user_sex = models.CharField(max_length=20)  # 性别
    user_age = models.IntegerField(null=True)  # 年龄
    phone=models.CharField(max_length=15,null=True)  # 电话号码
    id_no=models.CharField(max_length=20,null=True)  # 身份证号码
    role = models.CharField(max_length=20)  # 角色
    states=models.IntegerField(default=1)#权限
    c_time = models.DateTimeField(auto_now_add=True)  # 注册时间
class Userinfo(models.Model):#个人基本信息
    infoid = models.AutoField(primary_key=True)  # 信息编号
    uid = models.ForeignKey("User", on_delete=models.CASCADE)#所属
    user_name=models.CharField(max_length=20)#姓名
    user_sex=models.CharField(max_length=20)#性别
    user_age=models.CharField(max_length=20)#年龄
    user_height = models.FloatField()  # 身高
    user_weight = models.FloatField()  # 体重
    allergy = models.CharField(max_length=255)  # 药物过敏史
    illness = models.CharField(max_length=255)  # 疾病
    disability = models.CharField(max_length=255)  # 残疾情况
    common_drugs = models.CharField(max_length=255)  # 常用药
    c_time = models.DateTimeField(auto_now_add=True)  # 时间
class PEinfo(models.Model):#体检信息
    PEid = models.AutoField(primary_key=True)  # 信息编号
    uid = models.ForeignKey("User", on_delete=models.CASCADE)#所属用户
    user_name=models.CharField(max_length=20)#姓名
    user_sex=models.CharField(max_length=20)#性别
    hospital=models.CharField(max_length=20,null=True)#检查医院
    items=models.CharField(max_length=255)#检查项目
    blood_sugar=models.CharField(max_length=20)#血糖
    total_cholesterol=models.CharField(max_length=20)#总胆固醇
    triglyceride=models.CharField(max_length=20)#甘油三酯
    minimum=models.CharField(max_length=20)#低压
    maximum=models.CharField(max_length=20)#高压
    heart_rate=models.CharField(max_length=20)#心率
    date=models.DateTimeField(null=True)#体检日期
    c_time = models.DateTimeField(auto_now_add=True)  # 时间

class Visit(models.Model):#就诊记录
    vid = models.AutoField(primary_key=True)  # 信息编号
    uid = models.ForeignKey("User", on_delete=models.CASCADE)#所属
    user_name=models.CharField(max_length=20)#姓名
    user_sex=models.CharField(max_length=20)#性别
    department=models.CharField(max_length=20)#就诊科室
    chief_complaint=models.CharField(max_length=255)#主诉chief complaint
    HPI=models.CharField(max_length=255)#现病史history of present illness
    PH=models.CharField(max_length=255)#既往史 Past history
    diagnose=models.CharField(max_length=255)#诊断
    prescription=models.CharField(max_length=255)#处方药
    DA=models.CharField(max_length=255)#医嘱doctor's advice
    date=models.DateTimeField()#就诊日期
    c_time = models.DateTimeField(auto_now_add=True)  # 时间


class Health_doc(models.Model):#健康档案
    uid = models.ForeignKey("User", on_delete=models.CASCADE)
    user_height = models.FloatField()  # 身高
    user_weight = models.FloatField()  # 体重
    allergy = models.CharField(max_length=255)  # 药物过敏史
    illness = models.CharField(max_length=255)  # 疾病
    surgery = models.CharField(max_length=255)  # 手术
    injury = models.CharField(max_length=255)  # 外伤
    family_history = models.CharField(max_length=255)  # 家族史
    genetic_disease = models.CharField(max_length=255)  # 遗传病史
    disability = models.CharField(max_length=255)  # 残疾情况
    common_drugs = models.CharField(max_length=255)  # 常用药
    c_time = models.DateTimeField(auto_now_add=True)  # 时间

class Relative(models.Model):#亲属健康档案
    uid = models.ForeignKey("User", on_delete=models.CASCADE)
    # relative_name = models.CharField(max_length=20) #用户名
    # relative_sex= models.CharField(max_length=20) #	性别
    # relative_age= models.CharField(max_length=20) #	年龄
    id=models.AutoField(primary_key=True)#成员id
    relationship= models.CharField(max_length=20) #	与用户之间的关系
    relative_name= models.CharField(max_length=20) #	家属名
    relative_sex= models.CharField(max_length=20) #	家属性别
    relative_age= models.CharField(max_length=20) #	家属年龄
    relative_height= models.CharField(max_length=20) #	身高
    relative_weight= models.CharField(max_length=20) #	体重
    relative_allergy= models.CharField(max_length=255) #	药物过敏史
    relative_illness= models.CharField(max_length=255) #	疾病
    disability= models.CharField(max_length=255) #	残疾情况
    relative_surgery= models.CharField(max_length=255) #	手术
    relative_injury= models.CharField(max_length=255) #	外伤
    
    common_drugs = models.CharField(max_length=255,default="无")  # 常用药
    c_time = models.DateTimeField(auto_now_add=True)  # 注册时间
class Re_PEinfo(models.Model):#体检信息
    PEid = models.AutoField(primary_key=True)  # 信息编号
    uid = models.ForeignKey("Relative", on_delete=models.CASCADE)#所属用户
    items=models.CharField(max_length=255)#检查项目
    # hospital=models.CharField(max_length=20,null=True)#检查医院
    
    blood_sugar=models.CharField(max_length=20)#血糖
    total_cholesterol=models.CharField(max_length=20)#总胆固醇
    triglyceride=models.CharField(max_length=20)#甘油三酯
    minimum=models.CharField(max_length=20)#低压
    maximum=models.CharField(max_length=20)#高压
    heart_rate=models.CharField(max_length=20)#心率
    date=models.DateTimeField(null=True)#体检日期
    c_time = models.DateTimeField(auto_now_add=True)  # 时间

class Re_Visit(models.Model):#就诊记录
    vid = models.AutoField(primary_key=True)  # 信息编号
    uid = models.ForeignKey("Relative", on_delete=models.CASCADE)#所属
    department=models.CharField(max_length=20)#就诊科室
    chief_complaint=models.CharField(max_length=255)#主诉chief complaint
    HPI=models.CharField(max_length=255)#现病史history of present illness
    PH=models.CharField(max_length=255)#既往史 Past history
    diagnose=models.CharField(max_length=255)#诊断
    prescription=models.CharField(max_length=255)#处方药
    DA=models.CharField(max_length=255)#医嘱doctor's advice
    date=models.DateTimeField()#就诊日期
    c_time = models.DateTimeField(auto_now_add=True)  # 时间

from django.db import models

class CrawledContent(models.Model):
    title = models.CharField(max_length=255)  # 新闻标题字段，最大长度为255个字符
    link = models.URLField(unique=True)  # 新闻链接字段，唯一性约束，用于存储链接地址
