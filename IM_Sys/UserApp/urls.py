
from django.urls import path
from . import views

app_name = 'UserApp'

urlpatterns = [
    path("index/",views.personal_info,name="home"),#用户首页
    # path("home/",views.home,name="home"),#用户首页
    path("user_basic/",views.user_basic,name="user_basic"),#个人基本信息
    path("personal_manage/",views.personal_manage,name='personal_manage'),#个人健康档案管理
    path("personal_add/",views.personal_add,name="personal_add"),#个人健康档案添加
    path("family_manage/",views.family_manage,name='family_manage'),#家庭健康档案管理
    path("family_add/",views.family_add,name="family_add"),#家庭健康档案添加
    path("change_pwd/",views.change_pwd,name="change_pwd"),#修改密码
    path("blog/",views.blog,name="blog"),#论坛增删查改
    path("like_post/",views.like_post,name="like_post"),#点赞帖子
    path("blog_details/",views.blog_details,name="blog_details"),#论坛详情
    path("comment/",views.comment,name="comment"),#评论
    path("news/",views.news,name="news"),#新闻
    path("news_details/",views.news_details,name="news_details"),#新闻详情
    path("user_register/",views.user_register,name="user_register"),#我的预约
    path("register_online/",views.register_online,name="register_online"),#线上挂号
    path("online_consult/",views.online_consult,name="online_consult"),#线上咨询
    path("my_online_consult/",views.my_online_consult,name="my_online_consult"),#我的线上咨询
    path("answer/",views.answer,name="answer"),
    path('add_prescription/', views.add_prescription, name='add_prescription'),
    path('save_prescription/', views.save_prescription, name='save_prescription'),
path('get_doctors_by_department/<int:department_id>/', views.get_doctors_by_department, name='get_doctors_by_department'),
]