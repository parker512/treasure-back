# Generated by Django 5.1.7 on 2025-05-09 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='booklisting',
            name='author',
            field=models.CharField(default='Невідомий автор', max_length=255),
        ),
    ]
