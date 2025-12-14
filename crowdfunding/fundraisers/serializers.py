from rest_framework import serializers
from django.apps import apps


class PledgeSerializer(serializers.ModelSerializer):
    supporter = serializers.ReadOnlyField(source="supporter.id")

    class Meta:
        model = apps.get_model("fundraisers.Pledge")
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.amount = validated_data.get("amount", instance.amount)
        instance.comment = validated_data.get("comment", instance.comment)
        instance.anonymous = validated_data.get("anonymous", instance.anonymous)
        instance.fundraiser = validated_data.get("fundraiser", instance.fundraiser)
        instance.save()
        return instance
    
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.id")
    replies = serializers.SerializerMethodField()

    class Meta:
        model = apps.get_model("fundraisers.Comment")
        fields = "__all__"

    def get_replies(self, instance):
        replies = instance.replies.all()
        serializer = CommentSerializer(replies, many=True)
        return serializer.data

    def update(self, instance, validated_data):
        instance.content = validated_data.get("content", instance.content)
        instance.parent = validated_data.get("parent", instance.parent)
        instance.fundraiser = validated_data.get("fundraiser", instance.fundraiser)
        instance.save()
        return instance

class FundraiserSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.id")

    class Meta:
        model = apps.get_model("fundraisers.Fundraiser")
        fields = "__all__"


class FundraiserDetailSerializer(FundraiserSerializer):
    pledges = PledgeSerializer(many=True, read_only=True)

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get("description", instance.description)
        instance.goal = validated_data.get("goal", instance.goal)
        instance.image = validated_data.get("image", instance.image)
        instance.is_open = validated_data.get("is_open", instance.is_open)
        instance.save()
        return instance
    
