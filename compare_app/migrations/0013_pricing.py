# Generated by Django 3.1.1 on 2020-09-28 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compare_app', '0012_auto_20200928_2011'),
    ]

    operations = [
        migrations.CreateModel(
            name='pricing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('NAME', models.CharField(max_length=200)),
                ('WEIGHT', models.CharField(max_length=80)),
                ('OZ', models.FloatField()),
                ('PRICE_TEXT', models.CharField(max_length=20)),
                ('PRICE', models.FloatField()),
                ('PRICE_PER_OZ', models.CharField(max_length=20)),
                ('CURRENCY', models.CharField(max_length=10)),
                ('AVAILABILITY', models.CharField(max_length=100)),
                ('LINK', models.CharField(max_length=300)),
                ('LOAD_TIME', models.CharField(max_length=30)),
                ('SHOP', models.CharField(max_length=40)),
                ('IMG_LINK', models.CharField(max_length=300)),
                ('METAL', models.CharField(max_length=50)),
            ],
        ),
    ]
