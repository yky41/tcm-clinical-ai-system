
from django.urls import path
from . import views

app_name = 'DoctorApp'

urlpatterns = [
    path("index/",views.personal_info,name="doctor_index"),#首页
    path("change_pwd/",views.change_pwd,name="change_pwd"),#修改密码
    path("online_consult/",views.online_consult,name="online_consult"),#线上咨询 治疗
    path("register/",views.register,name="register"),#预约管理
    path("answer1/",views.answer1,name="answer1"),
    path('add_prescription/', views.add_prescription, name='add_prescription'),
    path('save_prescription/', views.save_prescription, name='save_prescription'),
# path('ask_medicine/', views.ask_medicine, name='ask_medicine'),
path("answer2/", views.answer2, name="answer2"),

]