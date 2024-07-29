# patients/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator, EmailValidator
from cryptography.fernet import Fernet
import base64
from django.conf import settings

# Retrieve the encryption key from environment variables
key = settings.ENCRYPTION_KEY.encode()  # Ensure it's in bytes format
cipher_suite = Fernet(key)

class PatientManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class Patient(AbstractBaseUser):
    name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    phone_number = models.CharField(max_length=10, validators=[RegexValidator(r'^\d{10}$')])
    address = models.CharField(max_length=255)
    emergency_contact_name = models.CharField(max_length=255)
    emergency_contact_relationship = models.CharField(max_length=50)
    emergency_contact_phone = models.CharField(max_length=10, validators=[RegexValidator(r'^\d{10}$')])
    emergency_contact_email = models.EmailField(validators=[EmailValidator()])
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
    policy_number = models.CharField(max_length=255)
    insurance_phone = models.CharField(max_length=10, validators=[RegexValidator(r'^\d{10}$')])
    consent_to_treat = models.BooleanField(default=False)
    privacy_policy = models.BooleanField(default=False)
    enable_2fa = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'date_of_birth', 'gender', 'phone_number', 'address']

    objects = PatientManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Encrypt sensitive fields before saving
        self.name = base64.urlsafe_b64encode(cipher_suite.encrypt(self.name.encode())).decode()
        self.phone_number = base64.urlsafe_b64encode(cipher_suite.encrypt(self.phone_number.encode())).decode()
        self.address = base64.urlsafe_b64encode(cipher_suite.encrypt(self.address.encode())).decode()
        self.emergency_contact_name = base64.urlsafe_b64encode(cipher_suite.encrypt(self.emergency_contact_name.encode())).decode()
        self.emergency_contact_phone = base64.urlsafe_b64encode(cipher_suite.encrypt(self.emergency_contact_phone.encode())).decode()
        super(Patient, self).save(*args, **kwargs)

