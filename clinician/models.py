# doctors/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator, EmailValidator
from cryptography.fernet import Fernet
import base64
from django.conf import settings

# Retrieve the encryption key from environment variables
key = settings.ENCRYPTION_KEY.encode()  # Ensure it's in bytes format
cipher_suite = Fernet(key)

class DoctorManager(BaseUserManager):
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

class Doctor(AbstractBaseUser):
    name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)  # Adjust max_length as needed
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    address = models.TextField(default='')
    emergency_contact_name = models.CharField(max_length=255)
    emergency_contact_relationship = models.CharField(max_length=255)
    emergency_contact_phone = models.CharField(max_length=20)
    emergency_contact_email = models.EmailField()
    medical_qualifications = models.TextField()
    years_of_experience = models.IntegerField()
    current_practice_location = models.CharField(max_length=255)
    professional_associations = models.TextField()
    research_interests = models.TextField()
    insurance_provider = models.CharField(max_length=255)
    policy_number = models.CharField(max_length=255)
    group_number = models.CharField(max_length=255)
    coverage_details = models.TextField()
    hospital_affiliation = models.CharField(max_length=255)
    languages_spoken = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    enable_2fa = models.BooleanField(default=False)
    
    # Metadata
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone_number', 'address']

    objects = DoctorManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Encrypt sensitive fields before saving
        self.name = base64.urlsafe_b64encode(cipher_suite.encrypt(self.name.encode())).decode()
        self.phone_number = base64.urlsafe_b64encode(cipher_suite.encrypt(self.phone_number.encode())).decode()
        super(Doctor, self).save(*args, **kwargs)
