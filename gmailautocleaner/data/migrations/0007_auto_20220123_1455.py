# Generated by Django 3.2.11 on 2022-01-23 19:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_celery_results', '0010_remove_duplicate_indices'),
        ('data', '0006_emailstorage_raw_emails_retrieval_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailstorage',
            name='task_id',
        ),
        migrations.AddField(
            model_name='emailstorage',
            name='task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='django_celery_results.taskresult'),
        ),
    ]
