# Generated by Django 4.2.2 on 2024-03-17 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0004_alter_player_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chessgame',
            name='status',
            field=models.CharField(choices=[('P', 'pending'), ('A', 'active'), ('F', 'finished')], default='P', max_length=1),
        ),
    ]
