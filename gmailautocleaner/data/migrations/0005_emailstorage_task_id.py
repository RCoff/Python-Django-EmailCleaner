# Generated by Django 3.2.11 on 2022-01-11 00:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0004_emailstorage_parse_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailstorage',
            name='task_id',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]