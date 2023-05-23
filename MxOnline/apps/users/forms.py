from django import forms
from captcha.fields import CaptchaField
import redis

from MxOnline.settings import REDIS_HOST, REDIS_PORT
from apps.users.models import UserProfile


# 修改手机号码的表单
class UpdateMobileForm(forms.Form):
    mobile = forms.CharField(required=True, min_length=11, max_length=11)
    code = forms.CharField(required=True, min_length=4, max_length=4)

    # 看验证码是否在数据库中(之前是否发送过验证码)
    def clean_code(self):
        mobile = self.data.get("mobile")
        code = self.data.get("code")
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset="utf8", decode_responses=True)
        redis_code = r.get(str(mobile))
        if code != redis_code:
            raise forms.ValidationError("验证码不正确")
        return self.cleaned_data


# 修改密码的表单
class ChangePwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=5)
    password2 = forms.CharField(required=True, min_length=5)

    def clean(self):
        pwd1 = self.cleaned_data["password1"]
        pwd2 = self.cleaned_data["password2"]

        if pwd1 != pwd2:
            raise forms.ValidationError("密码不一致")
        return self.cleaned_data


# 修改个人信息的表单
class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["nick_name", "gender", "birthday", "address"]


# 上传头像的表单
class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        # 只需要image字段
        fields = ["image"]


# 注册的表单
class RegisterGetForm(forms.Form):
    captcha = CaptchaField()


class RegisterPostForm(forms.Form):
    mobile = forms.CharField(required=True, min_length=11, max_length=11)
    # 验证码，设置为4位
    code = forms.CharField(required=True, min_length=4, max_length=4)
    password = forms.CharField(required=True)

    # 验证mobile
    def clean_mobile(self):
        mobile = self.data.get("mobile")
        # 验证手机号码是否已经注册
        users = UserProfile.objects.filter(mobile=mobile)
        # 若用户已经存在
        if users:
            # 抛出异常
            raise forms.ValidationError("该手机号码已注册")
        return mobile

    # 添加自己的验证逻辑，只验证code
    def clean_code(self):
        mobile = self.data.get("mobile")
        # 取出code
        code = self.data.get("code")
        # 在Redis中进行查询
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset="utf8", decode_responses=True)
        redis_code = r.get(str(mobile))
        # 若与redis中的code不相等
        if code != redis_code:
            # 抛出异常
            raise forms.ValidationError("验证码不正确")
        return code


# 继承Form类
class LoginForm(forms.Form):
    # 定义需要验证的表单字段，此处的字段名称要和views.py中的request.POST.get("username","")中一致也就是前端html中的input属性保持一致
    # required=True代表必填字段
    username = forms.CharField(required=True, min_length=2)
    password = forms.CharField(required=True, min_length=3)


class DynamicLoginForm(forms.Form):
    # 此mobile字段和static/js/login.j中url:"/send_sms/",data:{mobile保持一致
    # 最大最小都为11，就是只能输入11位的手机号
    mobile = forms.CharField(required=True, min_length=11, max_length=11)
    captcha = CaptchaField()


# 登录提交的Form
class DynamicLoginPostForm(forms.Form):
    mobile = forms.CharField(required=True, min_length=11, max_length=11)
    # 验证码，设置为4位
    code = forms.CharField(required=True, min_length=4, max_length=4)

    # 添加自己的验证逻辑，只验证code
    def clean_code(self):
        mobile = self.data.get("mobile")
        # 取出code
        code = self.data.get("code")
        # 在Redis中进行查询
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset="utf8", decode_responses=True)
        redis_code = r.get(str(mobile))
        # 若与redis中的code不相等
        if code != redis_code:
            # 抛出异常
            raise forms.ValidationError("验证码不正确")
        # 若相等
        return self.cleaned_data

    def clean(self):
        mobile = self.cleaned_data["mobile"]
        # 取出code
        code = self.cleaned_data["code"]
        # 在Redis中进行查询
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset="utf8", decode_responses=True)
        redis_code = r.get(str(mobile))
        # 若与redis中的code不相等
        if code != redis_code:
            # 抛出异常
            raise forms.ValidationError("验证码不正确")
        # 若相等
        return self.cleaned_data
