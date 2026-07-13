from django.db import models
from django.urls import reverse
class NamedModel(models.Model):
    name=models.CharField(max_length=120,unique=True)
    class Meta: abstract=True; ordering=['name']
    def __str__(self): return self.name
class Author(NamedModel): biography=models.TextField(blank=True)
class Category(NamedModel): description=models.TextField(blank=True)
class Publisher(NamedModel): website=models.URLField(blank=True)
class Book(models.Model):
    class Status(models.TextChoices): AVAILABLE='AVAILABLE','Available'; OUT='OUT','Out of stock'; ARCHIVED='ARCHIVED','Archived'
    title=models.CharField(max_length=255,db_index=True); author=models.ForeignKey(Author,on_delete=models.PROTECT,related_name='books'); category=models.ForeignKey(Category,on_delete=models.PROTECT,related_name='books'); publisher=models.ForeignKey(Publisher,on_delete=models.PROTECT,related_name='books')
    edition=models.CharField(max_length=60,blank=True); isbn=models.CharField(max_length=20,unique=True); language=models.CharField(max_length=50,default='English'); shelf_number=models.CharField(max_length=50,db_index=True); description=models.TextField(blank=True); cover_image=models.ImageField(upload_to='covers/',blank=True,null=True); available_copies=models.PositiveIntegerField(default=0); total_copies=models.PositiveIntegerField(default=1); status=models.CharField(max_length=10,choices=Status.choices,default=Status.AVAILABLE); qr_ready=models.BooleanField(default=True); barcode_ready=models.BooleanField(default=True); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['title']; indexes=[models.Index(fields=['title','isbn']),models.Index(fields=['category','status'])]
    def __str__(self): return self.title
    def get_absolute_url(self): return reverse('books:detail',args=[self.pk])
