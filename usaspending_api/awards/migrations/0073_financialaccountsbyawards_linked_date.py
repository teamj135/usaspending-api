# Generated by Django 2.2.14 on 2020-07-08 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('awards', '0072_auto_20200604_1725'),
    ]

    operations = [
        migrations.AddField(
            model_name='financialaccountsbyawards',
            name='linked_date',
            field=models.DateTimeField(null=True),
        ),
    ]