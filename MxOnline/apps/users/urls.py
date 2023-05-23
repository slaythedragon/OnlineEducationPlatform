from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from apps.users.views import UserInfoView, UploadImageView, ChangePwdView, ChangeMobileView
from apps.users.views import MyCourseView, MyFavOrgView, MyFavTeacherView, MyFavCourseView, MyMessageView


urlpatterns = [
    # 用户信息
    url(r'^info/$', UserInfoView.as_view(), name="info"),
    # 进行头像上传
    url(r'^image/upload/$', UploadImageView.as_view(), name="image"),
    # 密码修改
    url(r'^update/pwd/$', ChangePwdView.as_view(), name="update_pwd"),
    # 手机号码修改
    url(r'^update/mobile/$', ChangeMobileView.as_view(), name="update_mobile"),
    # 我的课程
    url(r'^mycourse/$', MyCourseView.as_view(), name="mycourse"),

    # # 或者可以不写MyCourseView，直接使用TemplateView，使用login_required来进行登录的验证，并传入current_page参数
    # url(r'^mycourse/$',login_required(TemplateView.as_view(template_name="usercenter-mycourse.html"), login_url="/login/"),{"current_page": "mycourse"}, name="mycourse"),

    # 我的收藏-课程机构
    url(r'^myfavorg/$', MyFavOrgView.as_view(), name="myfavorg"),
    # 我的收藏-授课教师
    url(r'^myfav_teacher/$', MyFavTeacherView.as_view(), name="myfav_teachers"),
    # 我的收藏-公开课程
    url(r'^myfav_course/$', MyFavCourseView.as_view(), name="myfav_course"),
    # 我的消息
    url(r'^messages/$', MyMessageView.as_view(), name="messages"),

]
