from django.urls import path
from . import views
app_name='books'
urlpatterns=[path('',views.book_list,name='list'),path('add/',views.book_edit,name='add'),path('<int:pk>/',views.detail,name='detail'),path('<int:pk>/edit/',views.book_edit,name='edit'),path('<int:pk>/delete/',views.book_delete,name='delete')]
for p,n,l,e,d in [('authors','author',views.authors,views.author_edit,views.author_delete),('categories','category',views.categories,views.category_edit,views.category_delete),('publishers','publisher',views.publishers,views.publisher_edit,views.publisher_delete)]: urlpatterns += [path(p+'/',l,name=p),path(p+'/add/',e,name=n+'_add'),path(p+'/<int:pk>/edit/',e,name=n+'_edit'),path(p+'/<int:pk>/delete/',d,name=n+'_delete')]
