# Generated by Django 3.1.3 on 2020-11-02 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0005_auto_20201102_1342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]