from django.views.generic import View
from django.http import JsonResponse
from django.shortcuts import render

from apps.operations.forms import UserFavForm, CommentsForm
from apps.operations.models import UserFavorite, CourseComments
from apps.courses.models import Course
from apps.organizations.models import CourseOrg, Teacher
from apps.operations.models import Banner


# Create your views here.

# 首页
class IndexView(View):
    def get(self, request, *args, **kwargs):
        # # 制造500的页面错误
        # 1/0
        # # 制造403错误页面
        # from django.core.exceptions import PermissionDenied
        # raise PermissionDenied
        banners = Banner.objects.all().order_by("index")
        # 将轮播图中已取出的课程进行过滤
        courses = Course.objects.filter(is_banner=False)[:6]
        # 轮播图课程
        banner_courses = Course.objects.filter(is_banner=True)
        course_orgs = CourseOrg.objects.all()[:15]

        return render(request, "index.html",{
            "banners": banners,
            "courses": courses,
            "banner_courses": banner_courses,
            "course_orgs": course_orgs
        })

# 课程评论
class CommentView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({
                "status": "fail",
                "msg": "用户未登录"
            })

        comment_form = CommentsForm(request.POST)
        if comment_form.is_valid():
            course = comment_form.cleaned_data["course"]
            comments = comment_form.cleaned_data["comments"]

            comment = CourseComments()
            comment.user = request.user
            comment.comments = comments
            comment.course = course
            comment.save()

            return JsonResponse({
                "status": "success",
            })
        # 若表单验证失败
        else:
            return JsonResponse({
                "status": "fail",
                "msg": "参数错误"
            })


# 用户收藏，取消收藏
class AddFavView(View):
    def post(self, request, *args, **kwargs):
        # 判断用户是否登录
        if not request.user.is_authenticated:
            # 若未登录，前端转跳到登录页面，对应templates/org_base.html中约146行
            return JsonResponse({
                "status": "fail",
                "msg": "用户未登录"
            })
        user_fav_form = UserFavForm(request.POST)
        if user_fav_form.is_valid():
            fav_id = user_fav_form.cleaned_data["fav_id"]
            fav_type = user_fav_form.cleaned_data["fav_type"]

            # 是否已经收藏
            existed_records = UserFavorite.objects.filter(user=request.user, fav_id=fav_id, fav_type=fav_type)
            # 若已经收藏
            if existed_records:
                # 再点击为取消收藏
                existed_records.delete()
                # 如果收藏的为课程
                if fav_type == 1:
                    course = Course.objects.get(id=fav_id)
                    # 将收藏数字段减1
                    course.fav_nums -= 1
                    # 保存到数据库中
                    course.save()
                # 如果收藏的为课程机构
                elif fav_type == 2:
                    course_org = CourseOrg.objects.get(id=fav_id)
                    # 将收藏数字段减1
                    course_org.fav_nums -= 1
                    # 保存到数据库中
                    course_org.save()
                # 如果收藏的为讲师
                elif fav_type == 3:
                    teacher = Teacher.objects.get(id=fav_id)
                    # 将收藏数字段减1
                    teacher.fav_nums -= 1
                    # 保存到数据库中
                    teacher.save()

                return JsonResponse({
                    "status": "success",
                    "msg": "收藏"
                })
            # 若还未收藏
            else:
                # 添加收藏记录
                user_fav = UserFavorite()
                user_fav.fav_id = fav_id
                user_fav.fav_type = fav_type
                user_fav.user = request.user
                user_fav.save()

                return JsonResponse({
                    "status": "success",
                    "msg": "已收藏"
                })
        # 若表单验证失败
        else:
            return JsonResponse({
                "status": "fail",
                "msg": "参数错误"
            })
