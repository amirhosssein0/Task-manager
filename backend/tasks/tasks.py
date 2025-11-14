from datetime import timedelta, date
from celery import shared_task
from django.utils import timezone

from .models import Task


@shared_task
def flag_overdue_tasks():
	"""
	Flag tasks that were due today but not completed.
	This runs every night at 9 PM to check tasks with due_date = today.
	"""
	today = timezone.localdate()
	# Only flag tasks that were due TODAY and are NOT completed
	# This way we only notify about tasks that should have been done today
	today_incomplete_qs = Task.objects.filter(
		completed=False, 
		due_date=today,
		overdue_notified=False  # Don't re-flag already notified tasks
	)
	today_count = today_incomplete_qs.count()
	today_incomplete_qs.update(overdue_notified=True)
	
	# Also flag tasks that are overdue (past due date)
	overdue_qs = Task.objects.filter(
		completed=False, 
		due_date__lt=today,
		overdue_notified=False
	)
	overdue_count = overdue_qs.count()
	overdue_qs.update(overdue_notified=True)
	
	# Return result for manual testing
	result = {
		'today_tasks_flagged': today_count,
		'overdue_tasks_flagged': overdue_count,
		'total_flagged': today_count + overdue_count,
		'date': today.isoformat()
	}
	print(f"✅ Flagged {today_count} tasks due today and {overdue_count} overdue tasks (Total: {result['total_flagged']})")
	return result


@shared_task
def create_recurring_tasks():
	"""
	Create new instances of recurring tasks.
	This runs daily to check for recurring tasks that need new instances created.
	"""
	today = timezone.localdate()
	created_count = 0
	
	# Find recurring tasks that need new instances
	# Either next_recurrence_date is today or in the past, or it's null and due_date is today/past
	recurring_tasks = Task.objects.filter(
		is_recurring=True,
		parent_task__isnull=True,  # Only process parent tasks, not instances
	).exclude(
		recurrence_type__isnull=True
	).exclude(
		recurrence_type=''
	)
	
	for parent_task in recurring_tasks:
		# Check if we should create a new instance
		should_create = False
		next_date = None
		
		# Check end conditions
		if parent_task.recurrence_end_date and today > parent_task.recurrence_end_date:
			continue  # Recurrence has ended
		
		if parent_task.recurrence_count and parent_task.recurrence_created_count >= parent_task.recurrence_count:
			continue  # Reached max count
		
		# Determine next date
		if parent_task.next_recurrence_date:
			next_date = parent_task.next_recurrence_date
			if next_date <= today:
				should_create = True
		else:
			# Calculate from due_date
			next_date = parent_task.calculate_next_recurrence()
			if next_date and next_date <= today:
				should_create = True
		
		if should_create and next_date:
			# Create new task instance
			new_task = Task.objects.create(
				user=parent_task.user,
				title=parent_task.title,
				description=parent_task.description,
				category=parent_task.category,
				label=parent_task.label,
				due_date=next_date,
				completed=False,
				is_recurring=False,  # Instances are not recurring
				parent_task=parent_task,
			)
			
			# Update parent task
			parent_task.recurrence_created_count += 1
			parent_task.next_recurrence_date = parent_task.calculate_next_recurrence()
			parent_task.save(update_fields=['recurrence_created_count', 'next_recurrence_date'])
			
			created_count += 1
	
	result = {
		'created_count': created_count,
		'date': today.isoformat()
	}
	if created_count > 0:
		print(f"✅ Created {created_count} recurring task instances")
	return result

