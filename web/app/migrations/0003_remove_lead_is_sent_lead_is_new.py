# Generated by Django 4.1 on 2022-09-11 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_lead_alter_worker_table'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lead',
            name='is_sent',
        ),
        migrations.AddField(
            model_name='lead',
            name='is_new',
            field=models.BooleanField(default=True),
        ),
    ]
