from django.conf.urls import url
from django.urls import path

from apps.courses.views import CourseListView, CourseDetailView, CourseLessonView, CourseCommentsView
from apps.courses.views import VideoView

urlpatterns = [
    # 课程列表页
    url(r'^list/$', CourseListView.as_view(), name="list"),
    # 课程详情页
    url(r'^(?P<course_id>\d+)/$', CourseDetailView.as_view(), name="detail"),
    # 课程章节信息
    url(r'^(?P<course_id>\d+)/lesson/$', CourseLessonView.as_view(), name="lesson"),
    # 课程评论
    url(r'^(?P<course_id>\d+)/comments/$', CourseCommentsView.as_view(), name="comments"),
    # 视频播放
    url(r'^(?P<course_id>\d+)/video/(?P<video_id>\d+)$', VideoView.as_view(), name="video"),
]
