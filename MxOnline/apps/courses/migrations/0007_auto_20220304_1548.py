# Generated by Django 2.2 on 2022-03-04 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_auto_20220228_1534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='url',
            field=models.CharField(max_length=1000, verbose_name='访问地址'),
        ),
    ]