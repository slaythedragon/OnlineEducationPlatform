"""MxOnline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path,re_path
from django.conf.urls import url, include
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve

import xadmin

from apps.users.views import LoginView, LogoutView, SendSmsView, DynamicLoginView, RegisterView
from apps.organizations.views import OrgView
from MxOnline.settings import MEDIA_ROOT
# from MxOnline.settings import STATIC_ROOT
from apps.operations.views import IndexView

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('xadmin/',xadmin.site.urls),
    # # 设置直接访问域名的时候直接到此页面
    # path('', TemplateView.as_view(template_name="index.html"), name="index"),
    # 首页
    path('', IndexView.as_view(), name="index"),
    # 在此处login后要加/，解决访问时http://127.0.0.1:8000/login后面多加/出现的Page not found的问题
    # path('login/', TemplateView.as_view(template_name="login.html"), name= "login")

    path('login/', LoginView.as_view(), name= "login"),
    # 注册
    path('register/', RegisterView.as_view(), name= "register"),
    # 动态登录
    path('d_login/', DynamicLoginView.as_view(), name= "d_login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    url(r'^captcha/', include('captcha.urls')),
    # 此处send_sms对应static/js/login.js中的url:"/send_sms/"接口
    # 去掉csrf_token的验证。报错误403，但使用之前的方式在form表单中末尾添加{% csrf_token %}的方式无效，因为并不是通过html直接提交，而是使用ajax异步的方式进行发送
    url(r'^send_sms/', csrf_exempt(SendSmsView.as_view()), name="send_sms"),
    # 配置上传文件访问的url,此正则表达式的意思为：将media后面的所有字符串截取出来放到path变量中
    url(r'media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    # # 静态文件配置
    # url(r'static/(?P<path>.*)$', serve, {"document_root": STATIC_ROOT}),
    # 机构相关页面
    # 进行子url的管理
    url(r'^org/', include(('apps.organizations.urls', "organizations"), namespace="org")),

    # 课程相关页面
    url(r'^course/', include(('apps.courses.urls', "courses"), namespace="course")),

    # 用户相关操作
    url(r'^op/', include(('apps.operations.urls', "operations"), namespace="op")),

    # 个人中心
    url(r'^users/', include(('apps.users.urls', "users"), namespace="users")),

]
