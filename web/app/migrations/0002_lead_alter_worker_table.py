# Generated by Django 4.1 on 2022-09-10 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lead',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('form_id', models.BigIntegerField()),
                ('created_time', models.DateTimeField()),
                ('name', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=14)),
                ('is_sent', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'leads',
            },
        ),
        migrations.AlterModelTable(
            name='worker',
            table='workers',
        ),
    ]