from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render
from books.models import Book
from transactions.models import Loan
@login_required
def home(request):
    loans=Loan.objects.select_related('book','student')
    if request.user.role in ('STUDENT','FACULTY'):
        mine=loans.filter(student=request.user); context={'student':True,'total_books':Book.objects.count(),'active_loans':mine.filter(status='ISSUED').count(),'pending':mine.filter(status='PENDING').count(),'fine':sum((x.calculate_fine() for x in mine.filter(status='ISSUED')),start=0),'recent':mine[:5],'notifications':request.user.notifications.filter(read=False)[:5]}
    else:
        groups=Book.objects.values('category__name').annotate(total=Count('id')).order_by('-total')[:6]; context={'total_books':Book.objects.count(),'available':Book.objects.filter(available_copies__gt=0).count(),'active_loans':loans.filter(status='ISSUED').count(),'pending':loans.filter(status='PENDING').count(),'recent':loans[:7],'chart_labels':[x['category__name'] for x in groups],'chart_values':[x['total'] for x in groups]}
    return render(request,'dashboard/home.html',context)
