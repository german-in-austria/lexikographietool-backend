from rest_framework import serializers

from .models import Post, Report
from account.serializers import UserNameSerializer


class PostSerializer(serializers.ModelSerializer):
    author = UserNameSerializer()
    is_author = serializers.SerializerMethodField()
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'text', 'parent', 'author', 'children','is_author','date_created', 'edited', 'children_count']



    def get_is_author(self,post):
        if 'request' not in self.context:
            return False
        return post.author == self.context['request'].user

    def get_children_count(self,post):
        return post.children.count()


class PostSimpleSerializer(serializers.ModelSerializer):
    author = UserNameSerializer()

    class Meta:
        model = Post
        fields = ['id', 'text', 'author','date_created']

class PostCreateSerializer(serializers.ModelSerializer):
    author = UserNameSerializer(read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'text', 'parent', 'author', 'lexeme']
class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
    post = PostSerializer()
    report_from = serializers.SerializerMethodField(read_only=True)
    reported_user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Report
        fields = '__all__'

    def get_report_from(self, report):
        return report.report_from.email

    def get_reported_user(self, report):
        return report.post.author.email
