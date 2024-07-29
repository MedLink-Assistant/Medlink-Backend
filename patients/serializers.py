# patients/serializers.py
from rest_framework import serializers
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

    def validate_phone_number(self, value):
        # Add custom validation logic for phone number if needed
        return value

    def validate_email(self, value):
        # Add custom validation logic for email if needed
        return value

    def create(self, validated_data):
        # Handle encryption and sanitization in the serializer
        return Patient.objects.create_user(**validated_data)
