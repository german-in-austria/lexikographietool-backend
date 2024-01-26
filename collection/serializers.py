from rest_framework import serializers

from .models import Collection
from lexeme.serializers import CardSerializer
from MyProject import rulemanager

class CollectionUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Collection
        fields = ['id','name','group', 'description','organization', 'public',
        'categories','can_add_lexemes_group','can_remove_lexemes_group','can_add_lexemes_public','can_remove_lexemes_public']

class CollectionSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField('get_username_by_author')
    # lexemes = CardSerializer(many=True, read_only=True)
    can_add_lexeme_to_collection = serializers.SerializerMethodField()
    can_remove_lexeme_from_collection = serializers.SerializerMethodField()
    is_owner=serializers.SerializerMethodField()
    count_lexemes = serializers.SerializerMethodField('get_count_lexemes')


    class Meta:
        model = Collection
        fields = ['id','name', 'username','group', 'description','organization', 'public',
        'categories','can_add_lexeme_to_collection','can_remove_lexeme_from_collection','count_lexemes','is_owner','can_add_lexemes_group', 'can_remove_lexemes_group' ,'can_add_lexemes_public', 'can_remove_lexemes_public']

    def get_username_by_author(self, collection):
        username = collection.author.username
        return username

    def get_can_add_lexeme_to_collection(self, collection):
        user = None
        if 'account' in self.context:
            user = self.context['account']
        return  rulemanager.can_add_lexeme_to_collection(collection,user)

    def get_can_remove_lexeme_from_collection(self, collection):
        user = None
        if 'account' in self.context:
            user = self.context['account']
        return  rulemanager.can_remove_lexeme_from_collection(collection,user)

    
    def get_is_owner(self,collection):
        if 'account' in self.context:
            return collection.author == self.context['account']

    def get_count_lexemes(self, collection):
        return collection.collectionlexeme_set.count()

class CollectionSimpleSerializer(serializers.ModelSerializer):
    groupname = serializers.SerializerMethodField('get_group_name')
    count_lexemes = serializers.SerializerMethodField('get_count_lexemes')

    class Meta:
        model = Collection
        fields = ['id','name', 'description','groupname','count_lexemes']

    def get_group_name(self, collection):
        if(collection.group):
            return collection.group.name
        return None

    def get_count_lexemes(self, collection):
        return collection.collectionlexeme_set.count()


class CollectionSimpleSerializerWithContainment(serializers.ModelSerializer):
    in_collection = serializers.SerializerMethodField('ifcontained')
    count_lexemes = serializers.SerializerMethodField('get_count_lexemes')

    class Meta:
        model = Collection
        fields = ['id','name', 'count_lexemes', 'description' ,'in_collection']

    def ifcontained(self, collection):
        if collection.lexemes.filter(id=self.context['lexeme_id']).exists():
            return True
        return False

    def get_count_lexemes(self, collection):
        return collection.collectionlexeme_set.count()