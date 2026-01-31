
from django.db import models
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "IM_Sys.IM_Sys.settings")
# Create your models here.


class Doctor(models.Model):#
    uid = models.AutoField(primary_key=True)  # 用户编号
    doctor_name = models.CharField(max_length=20)  # 用户名
    keshi = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=20)  # 邮箱
    password = models.CharField(max_length=20)  # 密码
    doctor_sex = models.CharField(max_length=20)  # 性别
    doctor_age = models.IntegerField()  # 年龄
    profile=models.TextField(default="/static/img/profile-img.jpg")#头像
    title = models.CharField(max_length=20)  # 职称	varchar
    deid = models.ForeignKey("Department", on_delete=models.CASCADE,null=True)  # 所属科室	varchar
    hospital = models.CharField(max_length=20)  # 所属医院	varchar
    role = models.CharField(max_length=20)  # 角色
    good_at=models.CharField(max_length=255,null=True)  # 擅长领域
    states=models.IntegerField(default=0)#权限
    c_time = models.DateTimeField(auto_now_add=True)  # 注册时间




class Department(models.Model):#所属科室
    id=models.AutoField(primary_key=True)
    d_name= models.CharField(max_length=255)#科室名称
    introduce=models.TextField(null=True)#科室介绍


class Recipe(models.Model):#处方
    recipe_id = models.AutoField(primary_key=True)  # 处方编号
    # d_id=models.ForeignKey("Doctor", on_delete=models.CASCADE,null=True)#所述医生编号
    # department = models.CharField(max_length=20)  # 科室
    date = models.DateTimeField(auto_now_add=True)  # 日期
    # u_id=models.ForeignKey("UserApp.User", on_delete=models.CASCADE,null=True)#用户编号
    # user_name = models.CharField(max_length=20)  # 病人姓名
    # user_sex = models.CharField(max_length=20)  # 性别
    # user_age = models.CharField(max_length=20)  # 年龄
    symptom = models.CharField(max_length=255)  # 症状
    diagnose = models.CharField(max_length=255)  # 诊断
    Rp = models.TextField()  # 药方
    c_time = models.DateTimeField(auto_now_add=True)  # 注册时间
class Consult(models.Model):#线上咨询信息
    c_id=models.AutoField(primary_key=True)#咨询信息编号
    d_id=models.ForeignKey("Doctor", on_delete=models.CASCADE)#医生编号
    u_id=models.ForeignKey("UserApp.User", on_delete=models.CASCADE)#用户编号
    r_id=models.ForeignKey("Recipe", on_delete=models.CASCADE,null=True)#处方编号
    # conent= models.TextField()  #内容
    target=models.TextField(null=True)#咨询目标
    howlong=models.TextField(null=True)#持续时间
    drugs=models.TextField(null=True)#药品
    status=models.IntegerField(null=True,default=0)#状态 0申请 1已回复
    c_time = models.DateTimeField(auto_now_add=True)  # 创建时间

class Register(models.Model):#挂号信息
    r_id=models.AutoField(primary_key=True)#挂号信息编号
    d_id=models.ForeignKey("Doctor", on_delete=models.CASCADE)#预约医生编号
    u_id=models.ForeignKey("UserApp.User", on_delete=models.CASCADE)#预约用户编号
    r_type=models.CharField(max_length=20,null=True) #挂号类型
    date=models.DateTimeField(null=True)#挂号时间
    s_time=models.CharField(max_length=20)#预约时间开始
    end_time=models.CharField(max_length=20)#预约时间结束
    status= models.TextField(default="0")  #状态
    c_time = models.DateTimeField(auto_now_add=True)  # 创建时间