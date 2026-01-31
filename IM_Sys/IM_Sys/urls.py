
"""IM_Sys URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include

from IM_Sys.views import home,login,register,test,logout,error

urlpatterns = [
    path('admin/', admin.site.urls),
    path("",home,name="home"),#首页
    path("login/",login,name="login"),#登录
    path("register/",register,name="register"),#注册
    path("logout/",logout,name="logout"),
    path("user/",include("UserApp.urls")),#用户
    path("doctor/",include("DoctorApp.urls")),#医生
    path("admin_sys/",include("adminApp.urls")),#管理员
    path("blog/",include("BlogApp.urls")),#博客
    path("error/",error,name="error"),
    path("test/",test,name="test"),
]
