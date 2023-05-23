import re

from django import forms
from apps.operations.models import UserAsk

# # 使用普通模式
# class AddAskForm(forms):
#     name = forms.CharField(required=True, min_length=2, max_length=20)
#     # 设置只能11位
#     mobile = forms.CharField(required=True, min_length=11, max_length=11)
#     course_name = forms.CharField(required=True, min_length=2, max_length=20)

# 使用modelform
class AddAskForm(forms.ModelForm):
    # UserAsk没有限制mobile长度，在此限制
    mobile = forms.CharField(max_length=11, min_length=11, required=True)
    # 指明继承哪个model
    class Meta:
        model = UserAsk
        # 指明将哪些字段生成form
        fields = ["name", "mobile", "course_name"]

    # 对字段进行表单验证
    # 验证手机号码是否合法
    def clean_mobile(self):
        mobile = self.cleaned_data["mobile"]
        # 正则表达式
        regx_mobile = "^1[358]\d{9}$|^147\d{8}$|^176\d{8}$"
        p = re.compile(regx_mobile)
        if p.match(mobile):
            return mobile
        else:
            raise forms.ValidationError("手机号码非法", code="mobile_invalid")