from rest_framework import serializers
from .models import Task, TaskTemplate, TaskTemplateItem


class TaskSerializer(serializers.ModelSerializer):
	class Meta:
		model = Task
		fields = (
			"id", "title", "description", "completed", "due_date", "category", "label", "created_at",
			"is_recurring", "recurrence_type", "recurrence_interval", "recurrence_days",
			"recurrence_end_date", "recurrence_count", "parent_task", "next_recurrence_date"
		)
		read_only_fields = ("id", "created_at", "parent_task", "next_recurrence_date")

	def validate(self, data):
		"""Clean up recurring fields for non-recurring tasks"""
		is_recurring = data.get('is_recurring', False)
		
		# If task is not recurring, clear recurring fields
		if not is_recurring:
			data['recurrence_type'] = None
			data['recurrence_interval'] = 1  # Keep default
			data['recurrence_days'] = []
			data['recurrence_end_date'] = None
			data['recurrence_count'] = None
		
		# Clean up empty strings to None for date fields
		if 'recurrence_end_date' in data:
			if data['recurrence_end_date'] == '':
				data['recurrence_end_date'] = None
		
		return data

	def to_internal_value(self, data):
		"""Convert empty strings and undefined to None for nullable fields"""
		# Handle recurrence_end_date: empty string -> None
		if 'recurrence_end_date' in data and data['recurrence_end_date'] == '':
			data['recurrence_end_date'] = None
		
		# Handle recurrence_count: undefined/null -> None
		if 'recurrence_count' in data and (data['recurrence_count'] is None or data['recurrence_count'] == ''):
			data['recurrence_count'] = None
		
		# Handle recurrence_type: if not recurring, set to None
		if 'is_recurring' in data and not data['is_recurring']:
			if 'recurrence_type' in data:
				data['recurrence_type'] = None
		
		return super().to_internal_value(data)

	def update(self, instance, validated_data):
		completed = validated_data.get("completed")
		if completed:
			validated_data["overdue_notified"] = False
		return super().update(instance, validated_data)


class TaskTemplateItemSerializer(serializers.ModelSerializer):
	class Meta:
		model = TaskTemplateItem
		fields = ("id", "title", "description", "category", "label", "due_date_offset", "order")
		read_only_fields = ("id",)


class TaskTemplateSerializer(serializers.ModelSerializer):
	items = TaskTemplateItemSerializer(many=True, read_only=True)
	
	class Meta:
		model = TaskTemplate
		fields = ("id", "name", "description", "category", "items", "created_at", "updated_at")
		read_only_fields = ("id", "created_at", "updated_at")


class TaskTemplateCreateSerializer(serializers.ModelSerializer):
	items = TaskTemplateItemSerializer(many=True, required=False)
	
	class Meta:
		model = TaskTemplate
		fields = ("name", "description", "category", "items")
	
	def create(self, validated_data):
		items_data = validated_data.pop("items", [])
		template = TaskTemplate.objects.create(**validated_data)
		for order, item_data in enumerate(items_data):
			# Remove 'order' from item_data if it exists to avoid duplicate
			item_data.pop('order', None)
			TaskTemplateItem.objects.create(template=template, order=order, **item_data)
		return template
	
	def update(self, instance, validated_data):
		items_data = validated_data.pop("items", None)
		for attr, value in validated_data.items():
			setattr(instance, attr, value)
		instance.save()
		
		if items_data is not None:
			# Delete existing items
			instance.items.all().delete()
			# Create new items
			for order, item_data in enumerate(items_data):
				# Remove 'order' from item_data if it exists to avoid duplicate
				item_data.pop('order', None)
				TaskTemplateItem.objects.create(template=instance, order=order, **item_data)
		
		return instance


