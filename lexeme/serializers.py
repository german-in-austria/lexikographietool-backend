from rest_framework import serializers

from .models import LexemeContent, Lexeme, Address, Report, Category, Example, Pronunciation, Etymology, LikeLexeme, LexemeContent
from rest_framework.fields import CurrentUserDefault
from django.db.models import Q
# Category
from collection.models import Collection,CollectionLexeme

from account.models import Account


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category']
        ordering = ['category']
        extra_kwargs = {
            'category': {'validators': []},
        }


# Address
# class ZipPlaceSerializer(serializers.ModelSerializer):
#     id = serializers.IntegerField()

#     class Meta:
#         model = Address
#         fields = ['id', 'zipcode', 'place', 'state']


# class StateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Address
#         fields = ['id', 'state']


# class AddressSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Address
#         fields = '__all__'
class LocationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id','name','state','country','osm_id','osm_value','latitude','longitude']
        
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id','name','state','country', 'latitude' ,'longitude']

    
# Example
class ExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Example
        fields = '__all__'


# Pronunciation
class PronunciationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pronunciation
        fields = '__all__'


# Etymology
class EtymologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Etymology
        fields = '__all__'



# Lexeme




class LexemeDetailSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True, validators=[])
    examples = ExampleSerializer(many=True, read_only=True)
    etymologies = EtymologySerializer(many=True, read_only=True)
    pronunciations = PronunciationSerializer(many=True, read_only=True)
    origin = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Lexeme
        fields = ['id', 'word', 'dialectWord', 'kind', 'description', 'origin',
                  'dialect', 'categories', 'etymologies', 'examples', 'pronunciations','sensitive']

        extra_kwargs = {
            'category': {'validators': []},
        }

    def get_username_from_author(selfself, lexeme):
        username = lexeme.author.username
        return username

    def get_origin(self, obj):
        if obj.origin == None:
            return None
        return obj.origin.state


class LexemeContentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LexemeContent
        fields = ['id', 'source', 'description', 'kind', 'origin', 'word', 'dialectWord', 'sensitive','lexeme','variety','genus']
       

class LexemeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lexeme
        fields = ['id','content']

        extra_kwargs = {
            'category': {'validators': []},
        }

    def get_username_from_author(self, lexeme):
        username = lexeme.author.username
        return username

    def get_origin(self, obj):
        
        if obj.origin == None:
            return None
        return obj.origin.state



class CardSerializer(serializers.ModelSerializer):
    word = serializers.SerializerMethodField(read_only=True)
    variety = serializers.SerializerMethodField(read_only=True)
    description = serializers.SerializerMethodField(read_only=True)
    kind = serializers.SerializerMethodField(read_only=True)
    genus = serializers.SerializerMethodField(read_only=True)
    dialectWord = serializers.SerializerMethodField(read_only=True)
    origin = serializers.SerializerMethodField(read_only=True)
    sensitive = serializers.SerializerMethodField(read_only=True)
    examples = serializers.SerializerMethodField(read_only=True)
    pronunciations = serializers.SerializerMethodField(read_only=True)
    etymologies = serializers.SerializerMethodField(read_only=True)
    categories = serializers.SerializerMethodField(read_only=True)
    source = serializers.SerializerMethodField(read_only=True)
    likes_amount = serializers.SerializerMethodField(read_only=True)
    liked = serializers.SerializerMethodField(read_only=True)

    author = serializers.SerializerMethodField(read_only=True)
    date_updated = serializers.SerializerMethodField(read_only=True)


    in_favorites = serializers.SerializerMethodField(read_only=True)
    in_collection = serializers.SerializerMethodField(read_only=True)
    is_author = serializers.SerializerMethodField(read_only=True)
    can_edit = serializers.SerializerMethodField(read_only=True)


    


    class Meta:
        model = Lexeme
        fields = '__all__'

    def get_word(self, obj):
        if not obj.content:
            return None
        return obj.content.word

    def get_variety(self, obj):
        if not obj.content:
            return None
        return obj.content.variety
    def get_description(self, obj):
        if not obj.content:
            return None
        return obj.content.description
    def get_kind(self, obj):
        if not obj.content:
            return None
        return obj.content.kind
    def get_genus(self, obj):
        if not obj.content:
            return None
        return obj.content.genus
    def get_dialectWord(self, obj):
        if not obj.content:
            return None
        return obj.content.dialectWord
    def get_sensitive(self, obj):
        if not obj.content:
            return None
        return obj.content.sensitive
    def get_examples(self, obj):
        if not obj.content:
            return None
        return ExampleSerializer(obj.content.examples, many=True).data
    def get_pronunciations(self, obj):
        if not obj.content:
            return None
        return PronunciationSerializer(obj.content.pronunciations, many=True).data
    def get_categories(self, obj):
        if not obj.content:
            return None
        return CategorySerializer(obj.content.categories, many=True).data
    def get_etymologies(self, obj):
        if not obj.content:
            return None
        return EtymologySerializer(obj.content.etymologies, many=True).data
    def get_source(self, obj):
        if not obj.content:
            return None
        return  obj.content.source

    def get_date_updated(self, obj):
        if not obj.content:
            return None
        return  obj.content.date_created
    


    def get_origin(self, obj):
        if not obj.content:
            return None
        return LocationSerializer(obj.content.origin).data

    def get_likes_amount(self, card):
        amount = card.likes.all().count()
        return amount

    def get_liked(self,card):
        request = self.context.get("request")
        if request and hasattr(request, "user") and hasattr(request.user, "favorite"):
            account = request.user
            like = LikeLexeme.objects.filter(Q(lexeme=card) & Q(user=account))
        
            if len(like) != 0:
                return like[0].like

        return False

    def get_in_favorites(self, card):

        request = self.context.get("request")
        if request and hasattr(request, "user") and hasattr(request.user, "favorite"):
            user = request.user

            # TODO: Rauslöschen
            if user and not hasattr(user.favorite, "lexemes"):
                favorite = Collection(name='Favoriten', author=user)
                favorite.save()
                user.favorite = favorite
                user.save()
            if user.favorite.lexemes.filter(id=card.id).exists():
                return True

        # if collection.lexemes.filter(id=self.context['lexeme_id']).exists():
        #    return True
        return False

    def get_in_collection(self, card):
        if 'collectionId' in self.context:

            collectionId = self.context['collectionId']
        else:
            return None
        if CollectionLexeme.objects.filter(Q(collection=collectionId)&Q(lexeme=card)).exists():

            return True

    def get_author(self, card):
        
        return card.author.username

    def get_is_author(self, card):
        if 'request' in self.context:
            request = self.context['request']
            if request.user == card.author:
                return True
        return False

    def get_can_edit(self, card):
        if 'request' in self.context:
            request = self.context['request']
            if request.user == card.author or request.user.is_superuser:
                return True
        return False


class LexemeSimpleSerializer(CardSerializer):
    class Meta:
        model = Lexeme
        fields = ['id','word','dialectWord','description']

class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
    lexeme = CardSerializer()
    report_from = serializers.SerializerMethodField(read_only=True)
    reported_user = serializers.SerializerMethodField(read_only=True)
    already_changed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Report
        fields = '__all__'


    def get_report_from(self, report):
        return report.report_from.email

    def get_reported_user(self, report):
        return report.lexeme.author.email

    def get_already_changed(self, report):
        if report.lexeme.content == report.content:
            return False
        return True


class HighscoreSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Account
        fields = ['username','count']

    def get_count(self, account):
        return account.lexemes__count