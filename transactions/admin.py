from django.contrib import admin
from .models import ActivityLog,Loan,Notification,Reservation
@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin): list_display=('book','student','status','due_date','fine_amount'); list_filter=('status',); search_fields=('book__title','student__username')
admin.site.register([Notification,Reservation,ActivityLog])
