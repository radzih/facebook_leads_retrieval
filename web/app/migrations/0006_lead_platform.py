# Generated by Django 4.1 on 2022-09-12 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_remove_lead_form_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='platform',
            field=models.CharField(default='sdf', max_length=255),
            preserve_default=False,
        ),
    ]
