from rest_framework import serializers
from .models import Artists, ArtistProfiles, Reviews
from user.serializers import UserSerializer
from django.contrib import messages

class ArtistSerializer(serializers.ModelSerializer):

    is_like = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)

    avatar = serializers.ImageField(use_url=True)
    bio_image = serializers.ImageField(use_url=True)
    bio_video = serializers.FileField(use_url=True)
    class Meta:
        model = Artists
        fields = "__all__"
        read_only_fields = ("id", "user", "activate", "credit", "level", "created", "updated")

    # def validate(self, data):
    #     if self.instance:
    #         score = data.get("score", self.instance.check_in)
    #         score = data.get("check_out", self.instance.check_out)
    #     else:
    #         check_in = data.get("check_in")
    #         check_out = data.get("check_out")
    #     if check_in == check_out:
    #         raise serializers.ValidationError("Not enough time between changes")
    #     return data

    def get_is_like(self, obj):
        request = self.context.get("request")
        if request:
            user = request.user
            if user.is_authenticated:
                return obj in user.artist_like.all()
        return False

    def create(self, validated_data):
        request = self.context.get("request")
        artist = Artists.objects.create(**validated_data, user=request.user)
        return artist
    # def validate_email(self, value):
    #     return value.upper()

    # def create(self, validated_data):
    #     credit = validated_data.get("credit")
    #     artist = super().create(validated_data)
    #     artist.credit =  "artist credit logic"
    #     artist.save()
    #     return artist        

class ReviewSerializer(serializers.ModelSerializer):

    is_like = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)
    class Meta:
        model = Reviews
        fields = "__all__"
        read_only_fields = ("id", "artist", "user")

    def validate(self, data):
        if self.instance:
            score = data.get("score", self.instance.score)
        else:
            score = data.get("score")

        if abs(self.instace.artist.get_artist_score-score) > 2:
                messages.info("평균 점수와 2점이상 차이납니다. 신중한 결정 부탁드립니다.")
        return data

    def get_is_like(self, obj):
        request = self.context.get("request")
        if request:
            user = request.user
            if user.is_authenticated:
                return obj in user.review_like.all()
        return False

    def create(self, validated_data):
        request = self.context.get("request")
        review = Reviews.objects.create(**validated_data, user=request.user)
        return review