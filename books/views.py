from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404,redirect,render
from accounts.decorators import roles_required
from .forms import AuthorForm,BookForm,CategoryForm,PublisherForm,style_form
from .models import Author,Book,Category,Publisher
@login_required
def book_list(request):
    qs=Book.objects.select_related('author','category','publisher'); q=request.GET.get('q',''); category=request.GET.get('category',''); status=request.GET.get('status','')
    if q: qs=qs.filter(Q(title__icontains=q)|Q(author__name__icontains=q)|Q(isbn__icontains=q))
    if category: qs=qs.filter(category_id=category)
    if status: qs=qs.filter(status=status)
    sort=request.GET.get('sort','title'); qs=qs.order_by(sort if sort.lstrip('-') in ('title','available_copies','created_at') else 'title')
    return render(request,'books/book_list.html',{'page_obj':Paginator(qs,10).get_page(request.GET.get('page')),'categories':Category.objects.all(),'q':q})
@login_required
def detail(request,pk): return render(request,'books/book_detail.html',{'book':get_object_or_404(Book.objects.select_related('author','category','publisher'),pk=pk)})
@roles_required('ADMIN','LIBRARIAN')
def book_edit(request,pk=None):
    obj=get_object_or_404(Book,pk=pk) if pk else None; form=style_form(BookForm(request.POST or None,request.FILES or None,instance=obj))
    if request.method=='POST' and form.is_valid(): form.save(); messages.success(request,'Book saved.'); return redirect('books:list')
    return render(request,'books/form.html',{'form':form,'title':('Edit' if obj else 'Add')+' Book'})
@roles_required('ADMIN','LIBRARIAN')
def book_delete(request,pk):
    obj=get_object_or_404(Book,pk=pk)
    if request.method=='POST': obj.delete(); messages.success(request,'Book deleted.'); return redirect('books:list')
    return render(request,'confirm_delete.html',{'object':obj})
def make_crud(model,form_class,label,plural):
    @roles_required('ADMIN','LIBRARIAN')
    def listing(request): return render(request,'books/simple_list.html',{'items':model.objects.all(),'label':label,'plural':plural})
    @roles_required('ADMIN','LIBRARIAN')
    def edit(request,pk=None):
        obj=get_object_or_404(model,pk=pk) if pk else None; form=style_form(form_class(request.POST or None,instance=obj))
        if request.method=='POST' and form.is_valid(): form.save(); messages.success(request,label+' saved.'); return redirect('books:'+plural)
        return render(request,'books/form.html',{'form':form,'title':('Edit' if obj else 'Add')+' '+label})
    @roles_required('ADMIN','LIBRARIAN')
    def delete(request,pk):
        obj=get_object_or_404(model,pk=pk)
        if request.method=='POST': obj.delete(); messages.success(request,label+' deleted.'); return redirect('books:'+plural)
        return render(request,'confirm_delete.html',{'object':obj})
    return listing,edit,delete
authors,author_edit,author_delete=make_crud(Author,AuthorForm,'Author','authors'); categories,category_edit,category_delete=make_crud(Category,CategoryForm,'Category','categories'); publishers,publisher_edit,publisher_delete=make_crud(Publisher,PublisherForm,'Publisher','publishers')
