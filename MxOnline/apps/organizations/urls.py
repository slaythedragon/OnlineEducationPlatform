from django.conf.urls import url
from django.urls import path
from apps.organizations.views import OrgView, AddAskView, OrgHomeView, OrgTeacherView, OrgCourseView, OrgDescView
from apps.organizations.views import TeacherListView, TeacherDetailView

urlpatterns = [
    # 代表以list结尾的数据
    url(r'^list/$', OrgView.as_view(), name="list"),
    url(r'^add_ask/$', AddAskView.as_view(), name="add_ask"),
    # 传递id，用正则表达式，取后边的数字
    url(r'^(?P<org_id>\d+)/$', OrgHomeView.as_view(), name="home"),
    # # 或者可以使用此种模式，效果相同
    # path('<int:org_id>/', OrgHomeView.as_view(), name= "home"),
    # 机构讲师页面
    url(r'^(?P<org_id>\d+)/teacher/$', OrgTeacherView.as_view(), name="teacher"),
    # 机构课程页面
    url(r'^(?P<org_id>\d+)/course/$', OrgCourseView.as_view(), name="course"),
    # 机构介绍页面
    url(r'^(?P<org_id>\d+)/desc/$', OrgDescView.as_view(), name="desc"),
    # 讲师列表页面
    url(r'^teachers/$', TeacherListView.as_view(), name="teachers"),
    # 讲师详情页面
    url(r'^teachers/(?P<teacher_id>\d+)/$', TeacherDetailView.as_view(), name="teacher_detail"),

]
