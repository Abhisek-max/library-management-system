from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display=('username','email','role','student_id','faculty_id','is_approved','is_active'); list_filter=('role','is_approved','is_active','department'); fieldsets=UserAdmin.fieldsets+(('Library profile',{'fields':('role','phone','department','student_id','faculty_id','is_approved','avatar')}),)
