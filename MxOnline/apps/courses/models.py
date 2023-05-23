# python默认带的库放最前面
from datetime import datetime

# 第三方库放中间，如Django
from django.db import models

# 最后放自己定义的类和方法
from apps.users.models import BaseModel
# 引入Teacher
from apps.organizations.models import Teacher
from apps.organizations.models import CourseOrg


# Create your models here.
"""
实体1 <关系> 实体2
一对多关系：
课程 章节 视频 课程资源
"""

"""
# 使用继承的机制来继承实体,这个类用来被继承，这样便不用重新写过多的列
# 继承models.Model
class BaseModel(models.Model):
   
    # 给每个数据添加一个添加的时间，用于做日志分析
    # 不能直接datetime.now()，这样记录的是Course类编译的时间
    # 而是希望记录生成实例时的时间course = Course(),只写方法名称，Django会在适当时间调用此方法
    
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        # 防止migration时，BaseModel生成表
        abstract = True
# 这个BaseModel可能会被operations和organizations中的model导入
# 所以要将BaseModel放到下一层，user层，将这段代码放到apps/users/models.py
"""

# 继承BaseModel
# 课程
class Course(BaseModel):
    # 添加外键
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="讲师")
    course_org = models.ForeignKey(CourseOrg, null=True, blank=True, on_delete=models.CASCADE, verbose_name="课程机构")
    # 实际的具体字段
    name = models.CharField(verbose_name="课程名", max_length=50)
    desc = models.CharField(verbose_name="课程描述", max_length=300)
    # 精确到分钟，要以最小单位去保存到数据库
    learn_times = models.IntegerField(default=0, verbose_name="学习时长(分钟数)")
    degree = models.CharField(verbose_name="难度", choices=(("cj", "初级"),("zj", "中级"),("gj", "高级")), max_length=2)
    students = models.IntegerField(default=0, verbose_name="学习人数")
    fav_nums = models.IntegerField(default=0, verbose_name="收藏人数")
    click_nums = models.IntegerField(default=0, verbose_name="点击数")
    notice = models.CharField(verbose_name="课程公告", max_length=300, default="")
    category = models.CharField(default=u"后端开发", max_length=20, verbose_name="课程类别")
    tag = models.CharField(default="", verbose_name="课程标签", max_length=10)
    youneed_know = models.CharField(default="", max_length=300, verbose_name="课程须知")
    teacher_tell = models.CharField(default="", max_length=300, verbose_name="老师告诉你")
    # 是否为经典课程
    is_classics = models.BooleanField(default=False, verbose_name="是否经典")
    # 显示富文本,TextField不限制长度
    detail = models.TextField(verbose_name="课程详情")
    # 是否为广告位课程
    is_banner = models.BooleanField(default=False, verbose_name="是否广告位")
    image = models.ImageField(upload_to="courses/%Y/%m", verbose_name="封面图", max_length=100)

    class Meta:
        verbose_name = "课程信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    # 动态统计章节数
    def lesson_nums(self):
        return self.lesson_set.all().count()


# 针对一个课程可能对应多个tag情况重新设计一张tag表
class CourseTag(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="课程")
    tag = models.CharField(max_length=100, verbose_name="标签")

    class Meta:
        verbose_name = "课程标签"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.tag


# 设计第二个实体，继承BaseModel
# 课程章节
class Lesson(BaseModel):
    # 设计外键,为上面定义的Course，必须指定on_delete属性，表示对应的外键数据被删除后，当前的数据应该怎么办
    # CASCADE()表示，若课程Course信息被删除，凡是外键指向当前这个课程的章节信息会被级联删除
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    # # 也可以写为：
    # course = models.ForeignKey(Course, on_delete=models.SET_NULL(), null=True, blank=True)

    name = models.CharField(max_length=100, verbose_name=u"章节名")
    learn_times = models.IntegerField(default=0, verbose_name=u"学习时长(分钟数)")

    class Meta:
        verbose_name = "课程章节"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name



# 设计第三个实体，继承BaseModel
# 课程视频
class Video(BaseModel):
    lesson = models.ForeignKey(Lesson, verbose_name="章节", on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name=u"视频名")
    learn_times = models.IntegerField(default=0, verbose_name=u"学习时长(分钟数)")
    url = models.CharField(max_length=1000, verbose_name=u"访问地址")

    class Meta:
        verbose_name = "视频"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

# 设计第四个实体，继承BaseModel
# 课程资源
class CourseResource(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="课程")
    name = models.CharField(max_length=100, verbose_name=u"名称")
    file = models.FileField(upload_to="course/resourse/%Y/%m", verbose_name="下载地址", max_length=200)


    class Meta:
        verbose_name = "课程资源"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name