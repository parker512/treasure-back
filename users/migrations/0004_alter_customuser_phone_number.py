# Generated by Django 5.1.7 on 2025-04-09 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_customuser_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(blank=True, default=0, max_length=20),
            preserve_default=False,
        ),
    ]
