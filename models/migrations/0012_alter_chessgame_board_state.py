# Generated by Django 4.2.2 on 2024-04-06 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0011_alter_chessgame_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chessgame',
            name='board_state',
            field=models.TextField(default='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR                             w KQkq - 0 1'),
        ),
    ]
