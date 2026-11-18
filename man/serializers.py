from rest_framework import serializers
from man.models import Gent


class GentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Gent
        fields = ("username", "password", "chat_id", "email")

    def create(self, validated_data):
        user = Gent.objects.create_user(
            username=validated_data["username"],
            chat_id=validated_data.get("chat_id", ""),
            password=validated_data["password"],
        )
        return user
