# Generated by Django 4.2.5 on 2023-09-17 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SolveGia', '0006_variant_median_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variant',
            name='median_rating',
            field=models.PositiveSmallIntegerField(),
        ),
    ]
