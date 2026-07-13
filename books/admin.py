from django.contrib import admin
from .models import Author,Book,Category,Publisher
@admin.register(Book)
class BookAdmin(admin.ModelAdmin): list_display=('title','author','category','available_copies','status'); list_filter=('status','category','language'); search_fields=('title','isbn','author__name')
admin.site.register([Author,Category,Publisher])
