from rest_framework import serializers
from .models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
	days_remaining = serializers.SerializerMethodField()

	class Meta:
		model = Subscription
		fields = ('plan', 'status', 'start_date', 'end_date', 'transaction_id', 'days_remaining')

	def get_days_remaining(self, obj: Subscription) -> int:
		return obj.days_remaining()


