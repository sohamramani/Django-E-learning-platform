# Generated by Django 5.2 on 2025-05-19 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edu_user', '0002_requestlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='otp',
            field=models.CharField(blank=True, max_length=6, null=True, verbose_name='otp'),
        ),
    ]
