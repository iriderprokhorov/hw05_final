# Generated by Django 2.2.16 on 2022-01-21 21:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_auto_20220121_2054'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('pk', '-pub_date'), 'verbose_name': 'Posts, it will be shown in admin panel'},
        ),
    ]