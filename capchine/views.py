from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from .forms import LoginForm, RegistrationForm, EditForm, RatingForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .token import account_activation_token
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.models import User
from .models import Student, Teacher, Search, SearchCode, Rating, Role, RatingCode
import random, string
import datetime
from django.utils import timezone
from datetime import date


# Create your views here.


@login_required
def user_logout(request):
    logout(request)
    return redirect('/login')



def user_login(request):
    if request.method=='POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            em = cd['username']
            usr = User.objects.filter(email = em)
            if len(usr)>0:
                usr = User.objects.get(email = em)
                em = usr.username


            user = authenticate(request, username = em,password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request,user)
                    messages.success(request, "Authenticated Successfully.")
                    return redirect("/")

                    return 
                else:
                    messages.error(request, "Disabled Account.")
                    return redirect('/login')
            else:
                messages.error(request, "Invalid login.")
                return redirect('/login')
    else:
        form = LoginForm()
        r_form = RegistrationForm()
    return render(request, 'registration/login_register.html',{'form':form,'r_form':r_form})


def user_registration(request):
    if request.method=='POST':
        user_form = RegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            u_name = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(20))
            chk_u = User.objects.filter(username = u_name)
            while len(chk_u)>0:
                u_name = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(20))
                chk_u = User.objects.filter(username = u_name)
            
            new_user.username = u_name
            new_user.is_active = False
            new_user.save()
            u_role = request.POST['role']
            print(u_role)
            if u_role =='student':
                Student.objects.create(u = new_user)
                Role.objects.create(u = new_user, my_role = 'student')
            else:
                Teacher.objects.create(u = new_user)
                Role.objects.create(u=new_user, my_role='teacher')


            current_site = get_current_site(request)
            email_subject = 'Activate Your Account'
            message = render_to_string('registration/activate_account.html', {
                'user': new_user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
                'token': account_activation_token.make_token(new_user),
            })
            to_email = user_form.cleaned_data.get('email')
            email = EmailMessage(email_subject, message, to=[to_email])
            email.send()
            return render(request, 'account/register_done.html',{'new_user':new_user})
        else:
            r_form = RegistrationForm()
            form = LoginForm()
            return render(request,'registration/login_register.html',{'r_form':r_form,'form':form})
    r_form = RegistrationForm()
    form = LoginForm()
    return render(request, 'registration/login_register.html',{'r_form':r_form,'form':form})


def activate_account(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('/')
    else:
        return HttpResponse('Activation link is invalid!')


@login_required
def student_dashboard(request):
    role = "Student"
    rating_codes = RatingCode.objects.filter(u = request.user)
    ratings = Rating.objects.filter(code__in = rating_codes.all())
    rc = RatingCode.objects.filter(u = request.user).order_by('-created')
    if len(rc)>0:
        rc = rc[0]

    sc = SearchCode.objects.filter(u = request.user).order_by('-created')
    if len(sc)>0:
        sc = sc[0]

        
    attnt = 0
    prfrm = 0
    punct = 0
    coop = 0
    count = 0
    for r in ratings:
        if r.attention:
            attnt += r.attention
            prfrm += r.performance
            punct += r.punctuality
            coop += r.cooperation
            count +=1 
            
    if count>0:
        attnt = attnt/ count
        prfrm = prfrm/ count
        punct = punct/ count
        coop = coop/ count
    return render(request, 'newbase.html',{'role':role,'attnt':attnt,'prfrm':prfrm,'punct':punct,'coop':coop, 'ratings':ratings,'sc':sc,'rc':rc})

            




@login_required
def teacher_dashboard(request):
    cd = None
    rating = False
    role = 'Teacher'
    rol = request.user.roly.my_role
    if rol == 'teacher':
        t = Teacher.objects.get(u = request.user)
        if t.search_count == None:
            search_count = 0
        else:
            search_count = t.search_count
    else:
        return redirect('/')
    rating_profiles = request.user.given_rating.filter(active=True).order_by('-created') 
    print('Rating Profiles: ',rating_profiles)
    searched_students = request.user.accessed_code.filter(created__lte= datetime.datetime.today(), created__gt=datetime.datetime.today() - datetime.timedelta(days=30)).order_by('-created')    
    return render(request, 'teacher_profile.html',{'role':role,'search_count':search_count,'cd':cd,'rating':rating,'rating_profiles':rating_profiles,'searched_students':searched_students})
	
	

@login_required
def dashboard(request):
    cd = None
    if request.user.is_superuser:
        return redirect('admin/')
    
    elif request.user.roly.my_role =='student':
        return redirect('student_dashboard/')
    else:
        return redirect('teacher_dashboard/')

    
        



@login_required
def edit(request):
    if request.method=='POST':
        user_form = EditForm(instance = request.user, data = request.POST)
        if user_form.is_valid():
            user_form.save()
            messages.success(request,"Changes saved successfully.")
            return redirect('/edit')
        else:
            messages.error(request,"Please enter correct values.")
            user_form = EditForm(instance = request.user)
    user_form = EditForm(instance = request.user)
    return render(request, 'new_edit.html',{'user_form':user_form})

from django.core.mail import send_mail

@login_required
def create_code(request):
    if request.user.roly.my_role != 'student':
        return redirect('/')
    random_code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(15))
    r = False
    if request.GET.get('rating') =='Yes':
        r = True
    srch_code = SearchCode.objects.create(u= request.user, code = random_code)
    subject = 'New Search Code Created'
    message = "Dear {}, \n\nYou have successfully created a new search code. Your new search code is: {}.".format(request.user.get_full_name(),srch_code.code)
    mail_sent = send_mail(subject, message, 'admin@project.com',[request.user.email])
    messages.success(request,"Search code generated.")

    return redirect('/')

@login_required
def rating_code(request):
    if request.user.roly.my_role != 'student':
        return redirect('/')
    random_code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(15))
    rating_code = RatingCode.objects.create(u = request.user, code=random_code) 
    subject = "New Rating Code Created"
    message = "Dear {}, \n\nYou have successfully created a new rating code. Your new rating code is: {}.".format(request.user.get_full_name(), rating_code.code)
    mail_sent = send_mail(subject, message, 'admin@project.com',[request.user.email])
    return redirect('/')


@login_required
def search(request):
    if request.user.roly.my_role != 'teacher':
        return redirect('/')
    return render(request,'search.html')




@login_required
def search_student(request):
    if request.user.roly.my_role !='teacher':
	    return redirect('/')
    s = request.GET.get('code')
    rtng = False
    rate_code = RatingCode.objects.filter(code = s)
    edt_rating = False
    if len(rate_code)>0:
        rc = ''
        rtng = True
        r = get_object_or_404(RatingCode, code = s)
        stdnt = r.u
        name = r.u.get_full_name()
        rgstrd = r.u.date_joined
        attnt = 0
        prfrm = 0
        punct = 0
        coop = 0
        count = 0
        ratings = []
        rooting = Rating.objects.filter(code = r)
        if len(rooting)>0:
            if not r.u.is_active:
                return HttpResponse("That student is banned.")
            rooting = Rating.objects.filter(code = r)
            tchr_in = rooting.filter(teacher = request.user)
            if len(tchr_in) > 0:
                edt_rating = True
            ratings = rooting
            for r in ratings:
                if r.attention:
                    attnt += r.attention
                    prfrm += r.performance
                    punct += r.punctuality
                    coop += r.cooperation
                    count +=1
            if count>0:
                attnt = attnt/count 
                prfrm = prfrm/count
                punct = punct/count
                coop = coop/count

    else:
        sc = get_object_or_404(SearchCode, code = s)
        now = timezone.now()
        diff = now - sc.created
        seconds = diff.seconds
        hours = seconds/60/60
        if hours >240.0:
            sc.active = False
            return HttpResponse("The code has been expired.")
        ratings = RatingCode.objects.filter(u = sc.u)
        ratings = Rating.objects.filter(code__in = ratings)
        stdnt = sc.u
        name = sc.u.get_full_name()
        rgstrd = sc.u.date_joined
        rc = ratings.order_by('-created')
        if len(rc)>0:
            rc = rc[0]
        attnt = 0
        prfrm = 0
        punct = 0
        coop = 0
        count = 0
        for r in ratings:
            if r.attention:
                attnt+= r.attention
                prfrm += r.performance
                punct += r.punctuality
                coop += r.cooperation
                count +=1
        if count> 0:
            attnt = attnt/count
            prfrm = prfrm/count
            punct = punct/count
            coop = coop/ count
        t = Teacher.objects.get(u = request.user)
        s_count = t.search_count
        if s_count == None:
            s_count = 0
        s_count +=1
        t.search_count = s_count
        t.save()
        ss = Search.objects.create(code = sc, accessed_by = request.user)
    role = 'Teacher'
    return render(request,'account/student_profile.html',{'role':role,'attnt':attnt,
    'prfrm':prfrm,'punct':punct,'coop':coop,'ratings':ratings,'rc':rc,'name':name,
    'rgstrd':rgstrd,'rtng':rtng,'stdnt':stdnt,'s':s,'edt_rating':edt_rating})














@login_required
def student_rating(request):
    if request.user.roly.my_role == 'teacher':
        r = request.GET.get('ratings')
        print(r)
        custId = request.GET.get('custId')
        code = request.GET.get('code')
        attnt = int(request.GET.get('attnt'))
        prfrm = int(request.GET.get('prfrm'))
        punct = int(request.GET.get('punct'))
        coop = int(request.GET.get('coop'))
        rating = attnt + prfrm + punct + coop
        rating = rating

        print('CustId: ',custId,'attnt: ',attnt,'prfrm: ',prfrm,'punct: ',punct,'coop: ',coop)
        u = get_object_or_404(User, username = custId)
        rate_code = get_object_or_404(RatingCode, code = code, u = u)
        rt = Rating.objects.filter(code = rate_code, teacher = request.user)
        if len(rt)>0:
            edit_rating = Rating.objects.get(code = rate_code, teacher = request.user)
            edit_rating.rating = rating
            edit_rating.attention = attnt
            edit_rating.performance = prfrm
            edit_rating.punctuality = punct
            edit_rating.cooperation = coop
            edit_rating.save()
            return redirect('teacher_dashboard')
        else:
            create_rating = Rating.objects.create(code = rate_code, teacher = request.user, rating = rating,
            attention = attnt, performance = prfrm, punctuality = punct, cooperation = coop)
            tt = Teacher.objects.get(u = request.user)
            t_count = tt.rating_count
            if t_count == None:
                t_count = 0
            t_count +=1
            print("T_count",t_count)
            tt.rating_count = t_count
            tt.save()
            return redirect('teacher_dashboard')
    else:
        return redirect('/')













def admin_student_code(request):
    if not request.user.is_superuser:
        return redirect('/')
    code = request.GET.get('code')
    s = SearchCode.objects.get(code = code)
    searches = Search.objects.filter(code = s)
    tchrz = []
    for s in searches:
        if s.accessed_by.username in tchrz:
            pass
        else:
            tchrz.append(s.accessed_by.username)
    tchrz_name = []
    for t in tchrz:
        u = User.objects.get(username = t)
        tchrz_name.append(u.get_full_name())

    print(tchrz_name)
    return render(request,'admin_student.html',{'tchrz_name':tchrz_name,'code':code})

