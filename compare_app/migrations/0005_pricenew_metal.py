# Generated by Django 3.1.1 on 2020-09-26 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compare_app', '0004_auto_20200925_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='pricenew',
            name='METAL',
            field=models.CharField(default='Silver', max_length=50),
            preserve_default=False,
        ),
    ]
