# Generated by Django 4.2.5 on 2023-09-22 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SolveGia', '0009_homework_variant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homework',
            name='results',
            field=models.ManyToManyField(blank=True, null=True, related_name='toresults', to='SolveGia.result'),
        ),
    ]
