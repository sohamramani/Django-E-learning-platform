# Generated by Django 5.2 on 2025-06-13 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edu_user', '0006_order_alter_userprofile_resume'),
    ]

    operations = [
        migrations.CreateModel(
            name='CashfreeOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(max_length=100, unique=True)),
                ('provider_order_id', models.CharField(blank=True, max_length=100, null=True)),
                ('payment_id', models.CharField(blank=True, max_length=100, null=True)),
                ('amount', models.FloatField()),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Success', 'Success'), ('Failure', 'Failure')], default='Pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
