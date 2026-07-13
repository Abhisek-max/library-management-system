from django import forms
from .models import Author,Book,Category,Publisher
def style_form(form):
    for f in form.fields.values(): f.widget.attrs.setdefault('class','form-control')
    return form
class BookForm(forms.ModelForm):
    class Meta: model=Book; fields='__all__'; widgets={'description':forms.Textarea(attrs={'rows':4})}
class AuthorForm(forms.ModelForm):
    class Meta: model=Author; fields='__all__'
class CategoryForm(forms.ModelForm):
    class Meta: model=Category; fields='__all__'
class PublisherForm(forms.ModelForm):
    class Meta: model=Publisher; fields='__all__'
