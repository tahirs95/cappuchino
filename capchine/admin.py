from django.contrib import admin
from .models import Student, Teacher, Search, Rating, Role, SearchCode, RatingCode
# Register your models here.


class StudentAdmin(admin.ModelAdmin): 

    list_display = ('u','total_ratings','inactive_search_codes','active_search_codes','created')
    

admin.site.register(Student, StudentAdmin)



class RoleAdmin(admin.ModelAdmin):
    list_display = ('u','my_role')
admin.site.register(Role,RoleAdmin)

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('u','search_count','search_codes_used','search_codes_usage_time','search_codes_used_till_now','rating_count','created')
    ordering = ['-search_count',]

admin.site.register(Teacher, TeacherAdmin)

class SearchCodeAdmin(admin.ModelAdmin):
    list_display = ('code','u','active','created')
admin.site.register(SearchCode, SearchCodeAdmin)

class SearchAdmin(admin.ModelAdmin):
    list_display = ('code','created')
admin.site.register(Search, SearchAdmin)

class RatingCodeAdmin(admin.ModelAdmin):
    list_display = ('code','u','created')
admin.site.register(RatingCode, RatingCodeAdmin)

class RatingAdmin(admin.ModelAdmin):
    list_display = ('code','rating','created')
admin.site.register(Rating, RatingAdmin)