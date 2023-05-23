from django.shortcuts import render
from django.views.generic.base import View
from pure_pagination import Paginator, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from apps.courses.models import Course, CourseTag, CourseResource, Video
from apps.operations.models import UserFavorite, UserCourse, CourseComments


# Create your views here.

# 视频播放
class VideoView(LoginRequiredMixin, View):
    login_url = "/login/"
    # url中配置了两个id，此处要接收两个参数
    def get(self, request, course_id, video_id, *args, **kwargs):
        """
        获取课程章节信息
        """
        course = Course.objects.get(id=int(course_id))
        course.click_nums += 1
        course.save()

        video = Video.objects.get(id=int(video_id))

        #查询用户是否已经关联了该课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

            course.students += 1
            course.save()

        #学习过该课程的所有同学
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        all_courses = UserCourse.objects.filter(user_id__in=user_ids).order_by("-course__click_nums")[:5]
        # related_courses = [user_course.course for user_course in all_courses if user_course.course.id != course.id]
        related_courses = []
        for item in all_courses:
            if item.course.id != course.id:
                related_courses.append(item.course)

        course_resources = CourseResource.objects.filter(course=course)

        return render(request, "course-play.html", {
            "course": course,
            "course_resources": course_resources,
            "related_courses": related_courses,
            "video": video,
        })

# 课程评论信息
# LoginRequiredMixin对view进行login登录的验证，可参考文档：https://docs.djangoproject.com/en/2.2/topics/auth/default/
class CourseCommentsView(LoginRequiredMixin, View):
    # 若未登录，指向的url
    login_url = "/login/"

    def get(self, request, course_id, *args, **kwargs):
        """
        获取课程章节信息
        """
        course = Course.objects.get(id=int(course_id))
        # 点击课程时，为课程增加点击数
        course.click_nums += 1
        course.save()

        # 课程评论
        comments = CourseComments.objects.filter(course=course)

        # 查询用户是否已经关联了课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        # 若没有查询到记录，则生成一条记录
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

            course.students += 1
            course.save()


        # 该课的同学还学过
        # 学习过该课程的所有同学
        user_courses = UserCourse.objects.filter(course=course)
        # 学过该课程的所有同学的id
        user_ids = [user_course.user.id for user_course in user_courses]
        all_courses = UserCourse.objects.filter(user_id__in=user_ids).order_by("-course__click_nums")[:5]
        related_courses = []
        for item in all_courses:
            # 去掉当前的课程
            if item.course.id != course.id:
                related_courses.append(item.course)
        # # 也可使用列表生成式
        # related_courses = [user_course.course for user_course in all_courses if user_course.course.id != course.id]

        # 课程资料的下载
        course_resources = CourseResource.objects.filter(course=course)

        return render(request, "course-comment.html", {
            "course": course,
            "course_resources": course_resources,
            "related_courses": related_courses,
            "comments": comments
        })


# 课程章节信息
# LoginRequiredMixin对view进行login登录的验证，可参考文档：https://docs.djangoproject.com/en/2.2/topics/auth/default/
class CourseLessonView(LoginRequiredMixin, View):
    # 若未登录，指向的url
    login_url = "/login/"

    def get(self, request, course_id, *args, **kwargs):
        """
        获取课程章节信息
        """
        course = Course.objects.get(id=int(course_id))
        # 点击课程时，为课程增加点击数
        course.click_nums += 1
        course.save()

        # 查询用户是否已经关联了课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        # 若没有查询到记录，则生成一条记录
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

            course.students += 1
            course.save()

        # 该课的同学还学过
        # 学习过该课程的所有同学
        user_courses = UserCourse.objects.filter(course=course)
        # 学过该课程的所有同学的id
        user_ids = [user_course.user.id for user_course in user_courses]
        all_courses = UserCourse.objects.filter(user_id__in=user_ids).order_by("-course__click_nums")[:5]
        related_courses = []
        for item in all_courses:
            # 去掉当前的课程
            if item.course.id != course.id:
                related_courses.append(item.course)
        # # 也可使用列表生成式
        # related_courses = [user_course.course for user_course in all_courses if user_course.course.id != course.id]

        # 课程资料的下载
        course_resources = CourseResource.objects.filter(course=course)
        return render(request, "course-video.html", {
            "course": course,
            "course_resources": course_resources,
            "related_courses": related_courses
        })


# 课程详情页面，获取课程详情
class CourseDetailView(View):
    def get(self, request, course_id, *args, **kwargs):
        course = Course.objects.get(id=int(course_id))
        # 点击课程时，为课程增加点击数
        course.click_nums += 1
        course.save()
        # 获取收藏状态
        # 是否收藏课程
        has_fav_course = False
        # 是否收藏课程机构
        has_fav_org = False
        # 判断用户是否登录
        if request.user.is_authenticated:
            # fav_type=1代表收藏的为课程
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True
            # fav_type=2代表收藏的为课程课程机构
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True

        # # 通过课程的tag做课程的推荐
        # tag = course.tag
        # related_courses = []
        # if tag:
        #     # 找标签相同的课程，取前3个。使用exclude方法排除当前课程，要去掉一批数据则使用__in，将列表中的数据全部去除
        #     related_courses = Course.objects.filter(tag=tag).exclude(id__in=[course.id])[:3]
        # 取到所有的tag
        tags = course.coursetag_set.all()
        # tag_list = []
        # for tag in tags:
        #     tag_list.append(tag.tag)
        tag_list = [tag.tag for tag in tags]
        course_tags = CourseTag.objects.filter(tag__in=tag_list).exclude(course__id=course.id)
        # 使用set，避免出现有多个tag的同一个课程重复显示
        related_courses = set()
        for course_tag in course_tags:
            related_courses.add(course_tag.course)

        return render(request, "course-detail.html", {
            "course": course,
            "has_fav_course": has_fav_course,
            "has_fav_org": has_fav_org,
            "related_courses": related_courses
        })


# 获取课程列表信息
class CourseListView(View):
    def get(self, request, *args, **kwargs):
        # 根据添加时间进行倒序排列，最新的放在最前面
        all_courses = Course.objects.order_by("-add_time")
        # 右边栏，热门课程的展示，进行切片只展示前3个
        hot_courses = Course.objects.order_by("-click_nums")[:3]

        # 搜索关键词
        keywords = request.GET.get("keywords", "")
        # 搜索类型
        s_type = "course"
        if keywords:
            # name__icontains前面的i代表不区别大小写，使用Q来进行语句的组装，使得任何一个字段出现keywords都可以被搜索
            all_courses = all_courses.filter(Q(name__icontains=keywords) | Q(desc__icontains=keywords) | Q(desc__icontains=keywords))

        # 课程排序
        # 如果未找到取空值
        sort = request.GET.get("sort", "")
        # 对应apps/courses/views.py中<<li class="{% if sort == 'students' %}active{% endif %}"><a href="?sort=students">参与人数</a></li>的参数
        if sort == "students":
            all_courses = all_courses.order_by("-students")
        elif sort == "hot":
            all_courses = all_courses.order_by("-click_nums")

        # 对课程机构数据进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_courses, per_page=1, request=request)
        courses = p.page(page)

        return render(request, "course-list.html", {
            "all_courses": courses,
            "sort": sort,
            "hot_courses": hot_courses,
            "keywords": keywords,
            "s_type": s_type
        })
