# Generated by Django 4.2.2 on 2024-03-17 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0005_alter_chessgame_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chessmove',
            name='promotion',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]
