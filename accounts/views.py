from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect,render
from .forms import FacultyRegistrationForm,LoginForm,StudentRegistrationForm,UserProfileForm,style_form
class UserLoginView(LoginView):
    template_name='accounts/login.html'; authentication_form=LoginForm
def register(request):
    if request.user.is_authenticated: return redirect('dashboard:home')
    form=style_form(StudentRegistrationForm(request.POST or None))
    if request.method=='POST' and form.is_valid():
        user=form.save(); login(request,user); messages.success(request,'Welcome! Your student account is ready.'); return redirect('dashboard:home')
    return render(request,'accounts/register.html',{'form':form,'account_type':'Student','alternate_url':'accounts:faculty_register','alternate_label':'Create faculty account'})
def faculty_register(request):
    if request.user.is_authenticated: return redirect('dashboard:home')
    form=style_form(FacultyRegistrationForm(request.POST or None))
    if request.method=='POST' and form.is_valid():
        user=form.save(); login(request,user); messages.success(request,'Welcome! Your faculty account is ready.'); return redirect('dashboard:home')
    return render(request,'accounts/register.html',{'form':form,'account_type':'Faculty','alternate_url':'accounts:register','alternate_label':'Create student account'})
@login_required
def profile(request):
    form=style_form(UserProfileForm(request.POST or None,request.FILES or None,instance=request.user))
    if request.method=='POST' and form.is_valid(): form.save(); messages.success(request,'Profile updated successfully.'); return redirect('accounts:profile')
    return render(request,'accounts/profile.html',{'form':form})
