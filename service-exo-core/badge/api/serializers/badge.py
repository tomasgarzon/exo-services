from rest_framework import serializers

from ...models import UserBadge, UserBadgeItem


class UserBadgeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBadgeItem
        fields = ['name', 'date']


class UserBadgeSerializer(serializers.ModelSerializer):
    order = serializers.CharField(source='badge.order')
    items = UserBadgeItemSerializer(many=True, source='user_badge_items')

    class Meta:
        model = UserBadge
        fields = [
            'code', 'category', 'num',
            'items', 'order', 'created',
        ]
