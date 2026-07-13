from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
from .models import User
def style_form(form):
    for field in form.fields.values(): field.widget.attrs.setdefault('class','form-control')
    return form
class LoginForm(AuthenticationForm):
    login_as=forms.ChoiceField(choices=(('STUDENT','Student'),('FACULTY','Faculty'),('LIBRARIAN','Librarian')),label='Sign in as',widget=forms.Select(attrs={'class':'form-select'}))
    def __init__(self,*args,**kwargs): super().__init__(*args,**kwargs); style_form(self)
    def clean(self):
        cleaned_data=super().clean(); user=self.get_user(); selected_role=cleaned_data.get('login_as')
        allowed_roles={'STUDENT':('STUDENT',),'FACULTY':('FACULTY',),'LIBRARIAN':('LIBRARIAN','ADMIN')}
        if user and selected_role and user.role not in allowed_roles[selected_role]: raise ValidationError('This account is not authorized for the selected sign-in type.')
        if user and not user.is_approved: raise ValidationError('Your faculty account is awaiting librarian approval.')
        return cleaned_data
class StudentRegistrationForm(UserCreationForm):
    email=forms.EmailField()
    class Meta:
        model=User
        fields=('first_name','last_name','email','username','student_id','department','phone','password1','password2')
        labels={'student_id':'Student registration number','department':'Branch / programme','phone':'Mobile number'}
    def save(self,commit=True):
        user=super().save(commit=False); user.role=User.Role.STUDENT
        if commit: user.save()
        return user
class FacultyRegistrationForm(UserCreationForm):
    email=forms.EmailField()
    class Meta:
        model=User
        fields=('first_name','last_name','email','username','faculty_id','department','phone','password1','password2')
        labels={'faculty_id':'Faculty ID','department':'Department','phone':'Mobile number'}
    def save(self,commit=True):
        user=super().save(commit=False); user.role=User.Role.FACULTY
        user.is_approved=False
        if commit: user.save()
        return user
class UserProfileForm(forms.ModelForm):
    class Meta: model=User; fields=('first_name','last_name','email','phone','department','avatar')
