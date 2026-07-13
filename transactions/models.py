from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone
from books.models import Book
class Loan(models.Model):
    class Status(models.TextChoices): PENDING='PENDING','Pending'; ISSUED='ISSUED','Issued'; RETURNED='RETURNED','Returned'; REJECTED='REJECTED','Rejected'
    student=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='loans'); book=models.ForeignKey(Book,on_delete=models.PROTECT,related_name='loans'); status=models.CharField(max_length=10,choices=Status.choices,default=Status.PENDING,db_index=True); requested_at=models.DateTimeField(auto_now_add=True); issued_at=models.DateTimeField(null=True,blank=True); due_date=models.DateField(null=True,blank=True); returned_at=models.DateTimeField(null=True,blank=True); renewals=models.PositiveSmallIntegerField(default=0); fine_amount=models.DecimalField(max_digits=8,decimal_places=2,default=0); notes=models.TextField(blank=True)
    class Meta: ordering=['-requested_at']; indexes=[models.Index(fields=['student','status']),models.Index(fields=['due_date','status'])]
    def calculate_fine(self): return self.fine_amount if self.status=='RETURNED' or not self.due_date else Decimal(max(0,(timezone.localdate()-self.due_date).days))*Decimal('2.00')
class Reservation(models.Model):
    student=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE); book=models.ForeignKey(Book,on_delete=models.CASCADE); created_at=models.DateTimeField(auto_now_add=True); active=models.BooleanField(default=True)
    class Meta: constraints=[models.UniqueConstraint(fields=['student','book'],name='unique_reservation')]
class Notification(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='notifications'); title=models.CharField(max_length=150); body=models.TextField(); read=models.BooleanField(default=False); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-created_at']
class ActivityLog(models.Model):
    actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name='activity_logs')
    action=models.CharField(max_length=120); details=models.TextField(blank=True); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-created_at']
    def __str__(self): return f'{self.action} at {self.created_at:%Y-%m-%d %H:%M}'
