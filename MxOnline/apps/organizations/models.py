from django.db import models

from apps.users.models import BaseModel
# Create your models here.


# 设计一个外键，在后台添加城市
class City(BaseModel):
    name = models.CharField(max_length=20, verbose_name=u"城市名")
    desc = models.CharField(max_length=200, verbose_name=u"描述")

    class Meta:
        verbose_name = "城市"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

# 继承BaseModel
# 课程机构
class CourseOrg(BaseModel):
    name = models.CharField(max_length=50, verbose_name="机构名称")
    # 课程描述为富文本，先暂时设为TextField()
    desc = models.TextField(verbose_name="描述")
    tag = models.CharField(default="pxjg", verbose_name="机构类别", max_length=4,
                           choices=(("pxjg","培训机构"), ("gr", "个人"), ("gx", "高校")))
    category = models.CharField(default="pxjg", verbose_name="机构类别", max_length=4,
                                choices=(("pxjg", "培训机构"), ("gr", "个人"), ("gx", "高校")))
    click_nums = models.IntegerField(default=0, verbose_name="点击数")
    fav_nums = models.IntegerField(default=0, verbose_name="收藏数")
    # 课程机构logo
    image = models.ImageField(upload_to="org/%Y/%m", verbose_name=u"logo", max_length=100)
    address = models.CharField(max_length=150, verbose_name="机构地址")
    students = models.IntegerField(default=0, verbose_name="学习人数")
    course_nums = models.IntegerField(default=0, verbose_name="课程数")

    # 是否为认证机构
    is_auth = models.BooleanField(default=False, verbose_name="是否认证")
    # 是否为金牌机构
    is_gold = models.BooleanField(default=False, verbose_name="是否金牌")


    # 设计一个外键，在后台添加城市
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name=u"所在城市")

    # 获取机构对应的课程
    def courses(self):
        # from apps.courses.models import Course
        # courses = Course.objects.filter(course_org=self)
        # return courses
        # 使用此属性course_set，避免相互import，前半部分course为model的名称，当前的model为CourseOrg是Course的外键，此时可以通过CourseOrg反向取到Course
        # 是否为经典课程，进行切片，防止数据显示出问题，设置只显示3个
        courses = self.course_set.filter(is_classics=True)[:3]
        return courses


    class Meta:
        verbose_name = "课程机构"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

# 课程讲师
class Teacher(BaseModel):
    org = models.ForeignKey(CourseOrg, on_delete=models.CASCADE, verbose_name="所属机构")
    name = models.CharField(max_length=50, verbose_name=u"教师名")
    work_years = models.IntegerField(default=0, verbose_name="工作年限")
    work_company = models.CharField(max_length=50, verbose_name="就职公司")
    work_position = models.CharField(max_length=50, verbose_name="公司职位")
    points = models.CharField(max_length=50, verbose_name="教学特点")
    click_nums = models.IntegerField(default=0, verbose_name="点击数")
    fav_nums = models.IntegerField(default=0, verbose_name="收藏数")
    age = models.IntegerField(default=18, verbose_name="年龄")
    image = models.ImageField(upload_to="teacher/%Y/%m", verbose_name="头像", max_length=100)

    class Meta:
        verbose_name = "教师"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    # 获取课程数量
    def course_nums(self):
        return self.course_set.all().count()
