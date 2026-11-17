from django.contrib.auth.models import User
from rest_framework import serializers

from advertisements.models import Advertisement, AdvertisementStatusChoices


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at',)
        read_only_fields = ('id', 'creator', 'created_at',)

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        request = self.context['request']
        user = request.user

        if not user.is_authenticated:
            return data

        status = data.get('status', getattr(self.instance, 'status', 'OPEN'))

        if status == AdvertisementStatusChoices.OPEN:
            qs = Advertisement.objects.filter(creator=user, status='OPEN')
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.count() >= 10:
                raise serializers.ValidationError({
                    'status': 'Не больше 10 открытых объявлений.'
                })

        return data
