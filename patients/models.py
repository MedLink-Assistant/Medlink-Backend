# patients/models.py
from django.db import models

class Patient(models.Model):
    name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    emergency_contact_name = models.CharField(max_length=255)
    emergency_contact_relationship = models.CharField(max_length=50)
    emergency_contact_phone = models.CharField(max_length=20)
    emergency_contact_email = models.EmailField()
    current_health_conditions = models.TextField()
    past_medical_history = models.TextField()
    allergies = models.TextField()
    current_medications = models.TextField()
    primary_care_physician = models.CharField(max_length=255)
    family_health_conditions = models.TextField()
    lifestyle_habits = models.TextField()
    exercise_routine = models.TextField()
    dietary_habits = models.TextField()
    insurance_provider = models.CharField(max_length=255)
    policy_number = models.CharField(max_length=50)
    insurance_phone = models.CharField(max_length=20)
    consent_to_treat = models.BooleanField()
    privacy_policy = models.BooleanField()
    password = models.CharField(max_length=255)
    enable_2fa = models.BooleanField()

    def __str__(self):
        return self.name
