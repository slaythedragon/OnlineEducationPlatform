from datetime import datetime

from django.db import models
# Django本身的用户抽象类
from django.contrib.auth.models import AbstractUser
# Create your models here.

# 定义自己的user，继承AbstractUser

# 设置性别选项，为元组类型,里面再写一个元组
GENDER_CHOICES = (
    ("male","男"),
    ("female","女")
)

# 使用继承的机制来继承实体,这个类用来被继承，这样便不用重新写过多的列
# 继承models.Model
class BaseModel(models.Model):
    """
    给每个数据添加一个添加的时间，用于做日志分析
    不能直接datetime.now()，这样记录的是Course类编译的时间
    而是希望记录生成实例时的时间course = Course(),只写方法名称，Django会在适当时间调用此方法
    """
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        # 防止migration时，BaseModel生成表
        abstract = True
# 这个BaseModel可能会被operations和organizations中的model导入
# 所以要将BaseModel放到下一层，user层，将这段代码放到apps/users/models.py


class UserProfile(AbstractUser):
    # Django已经自带用户名username和密码字段(为必填字段)，添加额外字段
    # 允许为空，允许不填 null=True, blank=True或者可替换为default=""表示默认为空字符串
    nick_name = models.CharField(max_length=50,verbose_name="昵称", default="")
    birthday = models.DateTimeField(verbose_name="生日", null=True, blank=True)
    gender = models.CharField(verbose_name="性别",choices=GENDER_CHOICES, max_length=6)
    address = models.CharField(max_length=100, verbose_name="地址",default="")
    # 系统默认使用手机号注册，所以不为空，而且要唯一
    mobile = models.CharField(max_length=11, verbose_name="手机号码")
    # 头像，upload_to为新建的media文件的子路径，会自动新建head_image目录,%Y/%m代表年月
    # ImageField本质上为CharField，将文件的路径保存到Field中,default设置默认头像
    image = models.ImageField(verbose_name="用户头像", upload_to="head_image/%Y/%m", default="default.jpg")

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def unread_nums(self):
        # 未读消息数量
        return self.usermessage_set.filter(has_read=False).count()

    # 得到UserProfile时，字符串的描述，直接输出时用
    def __str__(self):
        # 如果设置了昵称
        if self.nick_name:
            return self.nick_name
        else:
            # 继承的AbstractUser中的username(必填字段)
            return self.username