from django.db import migrations
 
def add_course_instructor(apps, schema_editor):
    Course = apps.get_model('course', 'Course')
    User = apps.get_model('users', 'User')
    # Here you can add logic to set relationships if needed
    # For example, assigning an instructor to existing courses, etc.
 
class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
        ('course', '0001_initial'),
    ]
 
    operations = [
        migrations.RunPython(add_course_instructor),
    ]