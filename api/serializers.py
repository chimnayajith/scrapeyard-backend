from rest_framework import serializers

class CarSerializer(serializers.Serializer):
    brand = serializers.CharField()
    model = serializers.CharField()
    manufacture_year = serializers.CharField()
    mileage = serializers.CharField()
    fuel_type = serializers.CharField()
    owner = serializers.CharField(default="N/A")
    price = serializers.CharField()
    emi = serializers.CharField(default="N/A")  
    url = serializers.URLField()
    image_url = serializers.URLField()
    source = serializers.CharField()
    location = serializers.DictField()
