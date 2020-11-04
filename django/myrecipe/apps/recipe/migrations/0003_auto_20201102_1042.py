# Generated by Django 3.1.3 on 2020-11-02 10:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipe', '0002_auto_20201102_1036'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='author',
        ),
        migrations.AddField(
            model_name='recipe',
            name='created_by',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recipe',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='recipe',
            name='updated_by',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]