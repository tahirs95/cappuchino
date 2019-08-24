from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.utils.html import mark_safe
# Create your models here.
ROLE_CHOICES = (
    ('student','Student'),
    ('teacher','Teacher'),
)
class Role(models.Model):
    u = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='roly')
    my_role = models.CharField(max_length=50, choices=ROLE_CHOICES, null = True, blank = True)

    def __str__(self):
        return self.u.get_full_name()
    


class Student(models.Model):
    u = models.ForeignKey(User,related_name="stdnt_info",on_delete=models.CASCADE)
    code_count = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(default=timezone.now)    

    def __str__(self):
        return self.u.get_full_name()
    
    def total_ratings(self):
        attnt = 0
        prfrm = 0
        punct = 0
        coop = 0
        count = 0
        rating_codes = RatingCode.objects.filter(u = self.u)
        ratings = Rating.objects.filter(code__in = rating_codes)
        for r in ratings:
            if r.attention:
                attnt += r.attention
                prfrm += r.performance
                punct += r.punctuality
                coop += r.cooperation
                count +=1
        total = attnt + prfrm + punct + coop
        return total 
    
    def inactive_search_codes(self):
        srch_codes = self.u.my_srch_code.filter(active = False)
        link = "http://127.0.0.1:8000/admin_student/?code="
        d = {}
        for s in srch_codes:
            new_link = link + str(s.code)
            d["m{0}".format(s.id)] = '<p><a href="{}">{}</a><p>'.format(new_link,s.code)
        keys = d.keys()
        for k in keys:
            k = d[k]
        a = d.values()
        l = ' '
        l = l.join(a)
        return mark_safe(l)
    inactive_search_codes.short_description = ('Inactive Codes')


    def active_search_codes(self):
        srch_codes = self.u.my_srch_code.filter(active = True)
        link = "http://127.0.0.1:8000/admin_student/?code="
        d = {}
        for s in srch_codes:
            new_link = link + str(s.code)
            d["m{0}".format(s.id)] = '<p><a href="{}">{}</a><p>'.format(new_link,s.code)
        keys = d.keys()
        for k in keys:
            k = d[k]
        a = d.values()
        l = ' '
        l = l.join(a)
        return mark_safe(l)
    active_search_codes.short_description = ('Active Code')




class Teacher(models.Model):
    u = models.ForeignKey(User, related_name="tchr_info",on_delete=models.CASCADE)
    search_count = models.IntegerField(blank=True, null = True)
    rating_count = models.IntegerField(blank = True, null = True)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.u.get_full_name()
    
    def search_codes_used(self):
        s = Search.objects.filter(accessed_by = self.u)
        l = []
        count = 0
        for ss in s:
            if ss.code.code in l:
                pass
            else:
                l.append(ss.code.code)
                count +=1
        return count


    def search_codes_usage_time(self):
        s = Search.objects.filter(accessed_by = self.u)
        usage_time = ''
        for ss in s:
            b = str(ss.created.time())
            b = b.split('.')
            b = b[0]
            usage_time = usage_time + b + ' '
        usage_time = '[' + usage_time + ']'
        return usage_time
    
    def search_codes_used_till_now(self):
        s = Search.objects.filter(accessed_by = self.u)
        l = []
        for ss in s:
            if ss.code.code in l:
                pass
            else:
                l.append(ss.code.code)
        return l

class SearchCode(models.Model):
    code = models.CharField(max_length = 200, blank = True, null = True)
    u = models.ForeignKey(User, related_name = 'my_srch_code', on_delete= models.CASCADE)
    active = models.BooleanField(default = True)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.code


class Search(models.Model):
    code = models.ForeignKey(SearchCode, related_name = 's_code', on_delete = models.CASCADE)
    accessed_by = models.ForeignKey(User, related_name = 'accessed_code', on_delete = models.CASCADE)
    #accessed_by = models.ManyToManyField(User, related_name='accessed_code',blank = True)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        code = self.code.code
        return code

class RatingCode(models.Model):
    code = models.CharField(max_length = 200, blank = True, null = True)
    u = models.ForeignKey(User, related_name = 'my_rating', on_delete = models.CASCADE)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.code


class Rating(models.Model):
    code = models.ForeignKey(RatingCode, related_name='rate_code', on_delete = models.CASCADE)
    teacher = models.ForeignKey(User, related_name="given_rating", on_delete=models.CASCADE, null = True, blank = True)
    #rated_by = models.ManyToManyField(User, related_name="given_rating",blank = True)
    rating = models.IntegerField(null = True, blank = True)
    attention = models.IntegerField(null = True, blank = True)
    performance = models.IntegerField(null = True, blank = True)
    punctuality = models.IntegerField(null = True, blank = True)
    cooperation = models.IntegerField(null = True, blank = True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(default=timezone.now)



    def __str__(self):
        code = self.code.code
        return code

