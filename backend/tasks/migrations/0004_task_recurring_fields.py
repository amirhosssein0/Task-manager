# Generated manually for recurring tasks and templates

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_task_overdue_notified'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='is_recurring',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='task',
            name='recurrence_type',
            field=models.CharField(blank=True, choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('yearly', 'Yearly'), ('custom', 'Custom')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='recurrence_interval',
            field=models.IntegerField(default=1, help_text='Every N days/weeks/months'),
        ),
        migrations.AddField(
            model_name='task',
            name='recurrence_days',
            field=models.JSONField(blank=True, default=list, help_text='Days of week for weekly recurrence [0=Monday, 6=Sunday]'),
        ),
        migrations.AddField(
            model_name='task',
            name='recurrence_end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='recurrence_count',
            field=models.IntegerField(blank=True, help_text='Number of occurrences', null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='recurrence_created_count',
            field=models.IntegerField(default=0, help_text='Number of tasks created so far'),
        ),
        migrations.AddField(
            model_name='task',
            name='parent_task',
            field=models.ForeignKey(blank=True, help_text='Original recurring task', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recurring_instances', to='tasks.task'),
        ),
        migrations.AddField(
            model_name='task',
            name='next_recurrence_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='TaskTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('category', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_templates', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TaskTemplateItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('category', models.CharField(blank=True, max_length=100)),
                ('label', models.CharField(choices=[('none', 'None'), ('yellow', 'Yellow'), ('green', 'Green'), ('blue', 'Blue'), ('red', 'Red')], default='none', max_length=12)),
                ('due_date_offset', models.IntegerField(default=0, help_text='Days offset from creation date (0 = same day, 1 = next day, etc.)')),
                ('order', models.IntegerField(default=0, help_text='Order of items in template')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='tasks.tasktemplate')),
            ],
            options={
                'ordering': ['order', 'id'],
            },
        ),
    ]

