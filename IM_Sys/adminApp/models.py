import django
from django.db import models

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "IM_Sys.IM_Sys.settings")

# Create your models here.
class Manager(models.Model):
    uid=models.AutoField(primary_key=True)#用户编号
    manager_name = models.CharField(max_length=20)#用户名
    email= models.CharField(max_length=20)#邮箱
    password= models.CharField(max_length=20)#密码
    manager_sex= models.CharField(max_length=20)#性别
    manager_age= models.IntegerField()#年龄
    role= models.CharField(max_length=20)#角色
    states=models.IntegerField(default=1)#权限
    c_time= models.DateTimeField(auto_now_add=True) #注册时间


