from rest_framework import serializers
from .models import User, Discipline, Material, MaterialRating


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'university', 'faculty', 'course', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class DisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discipline
        fields = '__all__'


class MaterialSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    discipline_title = serializers.ReadOnlyField(source='discipline.title')
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()

    class Meta:
        model = Material
        fields = [
            'id', 'title', 'description', 'material_type', 'file_attachment', 
            'external_url', 'discipline', 'discipline_title', 'author', 'author_name', 
            'created_at', 'download_count', 'is_verified', 'likes_count', 'dislikes_count'
        ]
        read_only_fields = ['author', 'download_count', 'is_verified']

    def get_likes_count(self, obj):
        return obj.ratings.filter(is_upvote=True).count()

    def get_dislikes_count(self, obj):
        return obj.ratings.filter(is_upvote=False).count()

    def validate(self, data):
        """Бизнес-валидация: в материале должен быть либо файл, либо ссылка"""
        if not data.get('file_attachment') and not data.get('external_url'):
            raise serializers.ValidationError("Необходимо загрузить файл или указать внешнюю URL-ссылку.")
        return data


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialRating
        fields = ['id', 'material', 'is_upvote', 'report_reason']
