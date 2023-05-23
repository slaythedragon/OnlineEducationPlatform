from django.shortcuts import render
from django.views.generic.base import View
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
import redis
from django.contrib.auth.mixins import LoginRequiredMixin
from pure_pagination import Paginator, PageNotAnInteger
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from apps.users.forms import LoginForm, DynamicLoginForm, DynamicLoginPostForm, UploadImageForm
from apps.users.forms import UserInfoForm, ChangePwdForm, UpdateMobileForm
from apps.users.forms import RegisterGetForm, RegisterPostForm
from apps.utils.AliSms import send_single_sms
from apps.utils.random_str import generate_random
from MxOnline.settings import REDIS_HOST, REDIS_PORT
from apps.users.models import UserProfile
from apps.operations.models import UserFavorite, UserMessage, Banner
from apps.organizations.models import CourseOrg, Teacher
from apps.courses.models import Course


# Create your views here.

# 自定义用户验证
class CustomAuth(ModelBackend):
    # 重载方法，会将之前在LoginView中的username和password传递进来
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 进行查询
            user = UserProfile.objects.get(Q(username=username)|Q(mobile=username))
            # 如果查询到用户，验证密码是否正确
            if user.check_password(password):
                return user
        # 未查询到
        except Exception as e:
            return None

# 未读消息，注入全局的html变量
def message_nums(request):
    """
    Add media-related context variables to the context.
    """
    if request.user.is_authenticated:
        return {'unread_nums': request.user.usermessage_set.filter(has_read=False).count()}
    else:
        return {}

# 我的消息
class MyMessageView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        messages = UserMessage.objects.filter(user=request.user)
        current_page = "message"
        # 进入我的消息页面后，将消息设置为已读
        for message in messages:
            message.has_read = True
            message.save()

        # 对消息进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(messages, per_page=1, request=request)
        messages = p.page(page)

        return render(request, "usercenter-message.html",{
            "messages": messages,
            "current_page": current_page
        })

# 我的收藏-公开课程
class MyFavCourseView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "myfav_course"
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            # 若课程id不存在，做异常处理
            try:
                course = Course.objects.get(id=fav_course.fav_id)
                course_list.append(course)
            except Course.DoesNotExist as e:
                pass
        return render(request, "usercenter-fav-course.html",{
            "course_list": course_list,
            "current_page": current_page
        })

# 我的收藏-授课教师
class MyFavTeacherView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "myfav_teacher"
        teacher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for fav_teacher in fav_teachers:
            org = Teacher.objects.get(id=fav_teacher.fav_id)
            teacher_list.append(org)
        return render(request, "usercenter-fav-teacher.html", {
            "teacher_list": teacher_list,
            "current_page": current_page
        })


# 我的收藏-课程机构
class MyFavOrgView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "myfavorg"
        org_list = []
        # 获取机构信息
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        for fav_org in fav_orgs:
            org = CourseOrg.objects.get(id=fav_org.fav_id)
            org_list.append(org)
        return render(request, "usercenter-fav-org.html", {
            "org_list": org_list,
            "current_page": current_page
        })


# 我的课程
class MyCourseView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        # 侧边栏选中状态的配置
        current_page = "mycourse"
        # my_courses = UserCourse.objects.filter(user=request.user)
        return render(request, "usercenter-mycourse.html", {
            # "my_courses": my_courses,
            "current_page": current_page
        })


# 修改手机号码
class ChangeMobileView(LoginRequiredMixin, View):
    login_url = "/login/"

    def post(self, request, *args, **kwargs):
        mobile_form = UpdateMobileForm(request.POST)
        if mobile_form.is_valid():
            mobile = mobile_form.cleaned_data["mobile"]
            # 已经存在的记录不能重复注册
            # if request.user.mobile == mobile:
            #     return JsonResponse({
            #         "mobile": "和当前号码一致"
            #     })
            if UserProfile.objects.filter(mobile=mobile):
                return JsonResponse({
                    "mobile": "该手机号码已经被占用"
                })
            # 进行修改
            user = request.user
            user.mobile = mobile
            # 将用户名也进行修改，否则登录会出现问题
            user.username = mobile
            user.save()
            return JsonResponse({
                "status": "success"
            })
        else:
            return JsonResponse(mobile_form.errors)
            # # 若需要修改后退出登录
            # logout(request)


# 进行密码的修改
class ChangePwdView(LoginRequiredMixin, View):
    login_url = "/login/"

    def post(self, request, *args, **kwargs):
        pwd_form = ChangePwdForm(request.POST)
        if pwd_form.is_valid():
            # # 判断两次输入密码是否一致，或将表单的验证放到form中完成
            # pwd1 = request.POST.get("password1", "")
            # pwd2 = request.POST.get("password2", "")
            #
            # if pwd1 != pwd2:
            #     return JsonResponse({
            #         "status":"fail",
            #         "msg":"密码不一致"
            #     })
            pwd1 = request.POST.get("password1", "")
            user = request.user
            user.set_password(pwd1)
            user.save()
            # # Django中修改完密码会自动退出，若不自动退出，使用以下方法
            # login(request, user)

            return JsonResponse({
                "status": "success"
            })
        else:
            return JsonResponse(pwd_form.errors)


# 进行头像的修改
class UploadImageView(LoginRequiredMixin, View):
    login_url = "/login/"

    # # 打开文件进行写入
    # def save_file(self, file):
    #     with open("C:/Users/Administrator/PycharmProjects/MxOnline/media/head_image/uploaded.jpg", "wb") as f:
    #         for chunk in file.chunks():
    #             f.write(chunk)

    def post(self, request, *args, **kwargs):
        # 处理用户上传的头像
        # 使用此modelform来进行文件的上传，可解决文件上传多次、文件保存路径写入到user、表单验证的功能,instance=request.user指明修改的实例
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        # 进行表单的验证
        if image_form.is_valid():
            image_form.save()
            return JsonResponse({
                "status": "success"
            })
        else:
            return JsonResponse({
                "status": "fail"
            })
        # files = request.FILES["image"]
        # self.save_file(files)


# 用户信息
class UserInfoView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "info"
        captcha_form = RegisterGetForm()
        return render(request, "usercenter-info.html", {
            "captcha_form": captcha_form,
            "current_page": current_page
        })

    def post(self, request, *args, **kwargs):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return JsonResponse({
                "status": "success"
            })
        else:
            return JsonResponse(user_info_form.errors)


# 用户注册
class RegisterView(View):
    def get(self, request, *args, **kwargs):
        register_get_form = RegisterGetForm()
        return render(request, "register.html", {
            "register_get_form": register_get_form
        })

    def post(self, request, *args, **kwargs):
        register_post_form = RegisterPostForm(request.POST)
        if register_post_form.is_valid():
            mobile = register_post_form.cleaned_data["mobile"]
            password = register_post_form.cleaned_data["password"]
            # 新建一个用户
            user = UserProfile(username=mobile)
            user.set_password(password)
            user.mobile = mobile
            user.save()
            # 进行登录
            login(request, user)
            # 跳转到首页
            return HttpResponseRedirect(reverse("index"))

        else:
            register_get_form = RegisterGetForm()
            return render(request, "register.html", {
                "register_get_form": register_get_form,
                "register_post_form": register_post_form
            })


# 动态验证码的登录
class DynamicLoginView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("index"))
        next = request.GET.get("next", "")
        login_form = DynamicLoginForm()
        banners = Banner.objects.all()[:3]
        return render(request, "login.html", {
            "login_form": login_form,
            "next": next,
            "banners": banners
        })

    def post(self, request, *args, **kwargs):
        login_form = DynamicLoginPostForm(request.POST)
        dynamic_login = True
        banners = Banner.objects.all()[:3]
        if login_form.is_valid():
            # 设置没有注册账号仍然可以登录
            # 先查询用户是否存在
            mobile = login_form.cleaned_data["mobile"]
            existed_users = UserProfile.objects.filter(mobile=mobile)
            if existed_users:
                user = existed_users[0]
            else:
                # 用户不存在，新建用户
                # 用户名为必填字段，用手机号填充
                user = UserProfile(username=mobile)
                # 此时用户未输入密码，可以进行密码的生成，生成10位
                password = generate_random(10, 2)
                # 密码为加密的，不能直接赋值明文，使用set_password方法进行密码的加密
                user.set_password(password)
                # 填入必填字段手机号
                user.mobile = mobile
                user.save()
            # 进行登录
            login(request, user)
            # 如果有next跳转到next，若没有则跳转到首页
            next = request.GET.get("next", "")
            if next:
                return HttpResponseRedirect(next)
            # 跳转到首页
            return HttpResponseRedirect(reverse("index"))
        else:
            d_form = DynamicLoginForm()
            return render(request, "login.html", {"login_form": login_form,
                                                  "d_form": d_form,
                                                  "banners": banners,
                                                  "dynamic_login": dynamic_login})


# 发送短信
class SendSmsView(View):
    def post(self, request, *args, **kwargs):
        send_sms_form = DynamicLoginForm(request.POST)
        re_dict = {}
        # 验证图片验证码是否正确
        if send_sms_form.is_valid():
            # 获取手机号码
            mobile = send_sms_form.cleaned_data["mobile"]
            # 随机生成数字验证码
            code = generate_random(4, 0)
            # 发送验证码
            re_json = send_single_sms(code, mobile=mobile)
            # 验证成功
            if re_json["body"]["Code"] == "OK":
                re_dict["status"] = "success"
                r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset="utf8", decode_responses=True)
                r.set(str(mobile), code)
                # 设置验证码5分钟过期,Redis的特性使得有新的验证码会覆盖之前的
                r.expire(str(mobile), 60 * 5)
            else:
                # 验证失败返回错误信息到前端进行显示
                re_dict["msg"] = re_json["body"]["Message"]
        else:
            # 表单验证失败,返回错误信息
            for key, value in send_sms_form.errors.items():
                re_dict[key] = value[0]

        # 将发送成功或失败的信息返回到前端，前端发起的是ajax请求，不能直接return render，需要使用jason数据进行交互
        return JsonResponse(re_dict)


# 注销
class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse("index"))


# 用户登录
# 继承Django内部的View
class LoginView(View):
    # 重载get方法，request为django自动注入的参数
    # 有可能传递多个参数，设置接受多变量的方式，可以点入View中从def dispatch中的return中查看源码
    def get(self, request, *args, **kwargs):
        # 在index.html已经判断了用户是否登录，获取此属性is_authenticated
        if request.user.is_authenticated:
            # 如果已经是登录状态，重定向到首页
            return HttpResponseRedirect(reverse("index"))

        banners = Banner.objects.all()[:3]
        next = request.GET.get("next", "")
        # 进行实例化
        login_form = DynamicLoginForm()
        return render(request, "login.html", {
            # 将变量传递进html中
            "login_form": login_form,
            "next": next,
            "banners": banners
        })

    # 用户数据的获取
    def post(self, request, *args, **kwargs):
        # 表单验证
        login_form = LoginForm(request.POST)
        banners = Banner.objects.all()[:3]
        if login_form.is_valid():

            # # 在页面上点击F12选中login.html中手机号/邮箱输入栏，可看到input name="username"，据此来进行获取
            # # 获取username，默认值为空
            # user_name = request.POST.get("username","")
            # password = request.POST.get("password","")

            # # 若用户名为空，没有必要执行之后的逻辑
            # if not user_name:
            #     return render(request, "login.html", {"msg": "请输入用户名"})
            # # 密码为空
            # if not password:
            #     return render(request, "login.html", {"msg": "请输入密码"})
            # if len(password) < 3:
            #     return render(request, "login.html", {"msg": "密码格式不正确"})
            # 用于通过用户名和密码查询用户是否存在，使用django内置的方法，因为数据库中存储的密码为密文，所以不能直接使用UserProfile来验证

            # 取出表单中的数据
            user_name = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]
            user = authenticate(username=user_name, password=password)
            if user is not None:
                # 若查询到用户，则进行登录
                # Django内部的login方法会自动完成cookie的设置
                login(request, user)
                # 如果有next跳转到next，若没有则跳转到首页
                next = request.GET.get("next", "")
                if next:
                    return HttpResponseRedirect(next)
                # 登录成功之后返回页面
                # reverse方法通过url的名称来定位url
                return HttpResponseRedirect(reverse("index"))
            else:
                # 未查询到用户,要将login_form传递回去，保留用户输入的错误的用户名和密码在页面上
                return render(request, "login.html", {"msg": "用户名或密码错误", "login_form": login_form, "banners": banners})
        else:
            return render(request, "login.html", {"login_form": login_form,
                                                  "banners": banners})
