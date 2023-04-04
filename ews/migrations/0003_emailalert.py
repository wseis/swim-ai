# Generated by Django 4.1.6 on 2023-04-04 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ews', '0002_delete_profile'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailAlert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('trigger_time', models.DateTimeField()),
                ('target', models.CharField(max_length=20)),
                ('catchment', models.CharField(max_length=10)),
            ],
        ),
    ]
