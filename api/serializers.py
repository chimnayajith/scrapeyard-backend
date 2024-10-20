from rest_framework import serializers

class CarSerializer(serializers.Serializer):
    car_name = serializers.CharField()
    manufacture_year = serializers.CharField()  # Ensure this matches the key in combined_data
    mileage = serializers.CharField()
    fuel_type = serializers.CharField()
    owner = serializers.CharField()
    price = serializers.CharField()
    emi = serializers.CharField()
    url = serializers.URLField()
    image_url = serializers.URLField()
