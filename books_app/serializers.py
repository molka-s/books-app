from rest_framework import serializers
from .models import User, Pret, Emprunt, Rating , Book

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'  
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class PretSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pret
        fields = '__all__'
        
class EmpruntSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emprunt
        fields = '__all__'   


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'