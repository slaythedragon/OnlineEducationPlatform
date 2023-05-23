from django.contrib import admin
# 使用Django自带的用户管理器
from django.contrib.auth.admin import UserAdmin
# Register your models here.

from apps.users.models import UserProfile

# 在后台新建一个管理器
# 继承类admin.ModelAdmin
class UserProfileAdmin(admin.ModelAdmin):
    pass

# 将表和管理器关联
# admin.site.register(UserProfile, UserProfileAdmin)

# 使用Django自带的用户管理器
admin.site.register(UserProfile, UserAdmin)