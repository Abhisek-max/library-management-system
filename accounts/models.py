from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
    class Role(models.TextChoices): ADMIN='ADMIN','Admin'; LIBRARIAN='LIBRARIAN','Librarian'; FACULTY='FACULTY','Faculty'; STUDENT='STUDENT','Student'
    role=models.CharField(max_length=12,choices=Role.choices,default=Role.STUDENT,db_index=True)
    phone=models.CharField(max_length=20,blank=True); department=models.CharField(max_length=100,blank=True); student_id=models.CharField(max_length=30,blank=True,unique=True,null=True); faculty_id=models.CharField(max_length=30,blank=True,unique=True,null=True); avatar=models.ImageField(upload_to='avatars/',blank=True,null=True); is_approved=models.BooleanField(default=True,db_index=True)
    def save(self,*args,**kwargs):
        if self.is_superuser: self.role=self.Role.ADMIN
        super().save(*args,**kwargs)
    @property
    def is_librarian(self): return self.role in (self.Role.ADMIN,self.Role.LIBRARIAN)
