# Generated by Django 3.1.1 on 2020-10-06 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compare_app', '0021_auto_20200928_2304'),
    ]

    operations = [
        migrations.DeleteModel(
            name='currencies',
        ),
        migrations.AlterField(
            model_name='pricings',
            name='AVAILABILITY',
            field=models.CharField(max_length=200),
        ),
    ]