# Generated by Django 2.2.16 on 2022-01-21 20:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_post_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-pub_date',), 'verbose_name': 'Posts, it will be shown in admin panel'},
        ),
    ]
