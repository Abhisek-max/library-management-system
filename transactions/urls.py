from django.urls import path
from . import views
app_name='transactions'
urlpatterns=[path('my-loans/',views.my_loans,name='my_loans'),path('request/<int:pk>/',views.request_loan,name='request'),path('reserve/<int:pk>/',views.reserve,name='reserve'),path('renew/<int:pk>/',views.renew,name='renew'),path('manage/',views.manage,name='manage'),path('quick-issue/',views.quick_issue,name='quick_issue'),path('members/',views.members,name='members'),path('members/<int:pk>/approve/',views.approve_member,name='approve_member'),path('reports/<str:format>/',views.reports,name='reports'),path('activity-log/',views.activity_log,name='activity_log'),path('<int:pk>/<str:action>/',views.action,name='action'),path('notifications/',views.notifications,name='notifications')]
