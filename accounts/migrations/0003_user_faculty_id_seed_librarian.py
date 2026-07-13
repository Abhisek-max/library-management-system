from django.db import migrations, models
from django.contrib.auth.hashers import make_password

def create_initial_librarian(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    if not User.objects.filter(username='admin').exists():
        User.objects.create(
            username='admin', email='admin@library.local', first_name='Library', last_name='Administrator',
            role='ADMIN', is_staff=True, is_superuser=True, is_active=True,
            password=make_password('admin123'),
        )

class Migration(migrations.Migration):
    dependencies = [('accounts', '0002_alter_user_role')]
    operations = [
        migrations.AddField(model_name='user', name='faculty_id', field=models.CharField(blank=True, max_length=30, null=True, unique=True)),
        migrations.RunPython(create_initial_librarian, migrations.RunPython.noop),
    ]
