import xadmin

from apps.organizations.models import Teacher,CourseOrg,City

class TeacherAdmin(object):
    list_display = ['org', 'name', 'work_years', 'work_company']
    search_fields = ['org', 'name', 'work_years', 'work_company']
    list_filter = ['org', 'name', 'work_years', 'work_company']

class CourseOrgAdmin(object):
    list_display = ['name', 'desc', 'click_nums', 'fav_nums']
    search_fields = ['name', 'desc', 'click_nums', 'fav_nums']
    list_filter = ['name', 'desc', 'click_nums', 'fav_nums']

class CityAdmin(object):
    # 列表页显示的字段名称，要和models中对应
    list_display = ["id", "name", "desc"]
    # 根据什么字段进行搜索
    search_fields = ["name", "desc"]
    # 根据什么字段进行过滤
    list_filter = ["name", "desc", "add_time"]
    # 根据什么字段在页面上直接进行编辑
    list_editable = ["name", "desc"]

xadmin.site.register(Teacher, TeacherAdmin)
xadmin.site.register(CourseOrg, CourseOrgAdmin)
xadmin.site.register(City, CityAdmin)