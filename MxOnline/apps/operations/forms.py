import re

from django import forms
from apps.operations.models import UserFavorite, CourseComments

# 使用modelform
class UserFavForm(forms.ModelForm):
    # 指明继承哪个model
    class Meta:
        model = UserFavorite
        # 指明将哪些字段生成form
        fields = ["fav_id", "fav_type"]


class CommentsForm(forms.ModelForm):
    # 指明继承哪个model
    class Meta:
        model = CourseComments
        # 指明将哪些字段生成form
        fields = ["course", "comments"]
