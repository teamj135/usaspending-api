# Generated by Django 2.2.12 on 2020-06-10 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('references', '0044_disasteremergencyfundcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='disasteremergencyfundcode',
            name='urls',
            field=models.TextField(null=True),
        ),
    ]