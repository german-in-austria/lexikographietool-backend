import string

from .models import Account
from rest_framework import serializers

from collection.models import Collection

from lexeme.models import Address

class LocationCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=False)
    class Meta:
        model = Address
        fields = ['id','name','state','country','osm_id','osm_value','latitude','longitude']
        
class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = Account
        fields = ['email', 'username', 'password', 'password2', 'home','age']

        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        account = Account(
            email=self.validated_data['email'].lower(),
            username=self.validated_data['username'],
            age=self.validated_data['age'],
            home=self.validated_data['home'],

        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        account.set_password(password)
        account.save()
        favorite = Collection(name='Favoriten', author = account)
        favorite.save()
        account.favorite = favorite
        account.save()
        return account

class UserSerializer(serializers.ModelSerializer):
    home = LocationCreateSerializer()
    locations = LocationCreateSerializer(many=True)

    class Meta:
        model = Account
        fields = ['email', 'username', 'home','age','locations','show_sensitive_words', 'is_superuser']


    def update(self, instance, validated_data):
        print(validated_data['home']['id'])

        home = Address.objects.get(pk =validated_data['home']['id'])

        location_list = [item['id'] for item in validated_data['locations']]

        locations = Address.objects.filter(pk__in=location_list)
        instance.locations.set(locations)   
        instance.username=validated_data['username']
        print(instance.username)
        instance.age=validated_data['age']
        instance.home = home
        instance.show_sensitive_words = validated_data['show_sensitive_words']
        instance.save()
        return instance

class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['username']


class UpdatePasswordSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = Account
        fields = ['username','email','password','password2']

    def update(self, instance, validated_data):
        user= self.context['request'].user
        if user.pk != instance.pk:
            raise serializers.ValidationError({"authorize": "You dont have permission for this user."})
        instance.set_password(validated_data['password'])

        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        instance.set_password(password)
        instance.save()
        return instance



