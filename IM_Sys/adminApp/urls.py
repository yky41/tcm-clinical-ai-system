
from django.urls import path
import IM_Sys.views
from adminApp import views
app_name = 'adminApp'

urlpatterns = [
    path("index/",views.personal_info,name="admin_index"),#管理员首页
    path("change_pwd/",views.change_pwd,name="change_pwd"),#修改密码
    path("user_manage/",views.user_manage,name="user_manage"),#用户管理
    path("user_manage1/",views.user_manage1,name="user_manage1"),#用户管理
    path("user_manage2/",views.user_manage2,name="user_manage2"),#用户管理
    path("doctor_manage/",views.doctor_manage,name="doctor_manage"),#医生管理
    path("patient_manage/",views.user_manage2,name="patient"),#医生管理
    path("health_news/",views.health_news,name="health_news"),#健康咨询管理
    path("discuss_manage/",views.blog_manage,name="discuss_manage"),#论坛管理
    path("discuss_manage/",views.blog_manage,name="discuss_manage"),#论坛管理
    path("edit_doctor_info/",views.edit_doctor_info,name="edit_doctor_info"),
    path("keshi/",views.keshi,name="keshi"),
    path("info/",views.info,name="info"),
    path('info/edit/<int:infoid>/', views.ehi, name='ehi'),
    path('keshi/add/', views.add_department, name='add_department'),
    path('keshi/delete/', views.delete_department, name='delete_department'),
    path('info/<int:PEid>/', views.ehi1, name='ehi1'),
    path('info/ed/<int:vid>/', views.ehi2, name='ehi2'),





]