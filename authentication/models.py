from django.conf import settings
from cryptography.fernet import Fernet
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Initialize the cipher suite with the encryption key from settings
cipher_suite = Fernet(settings.ENCRYPTION_KEY)

class UserManager(BaseUserManager):
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

class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    otp_secret = models.CharField(max_length=16, blank=True, null=True)
    enable_2fa = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    
    def generate_otp_secret(self):
        self.otp_secret = Fernet.generate_key().decode()
        self.save()
    
    def verify_otp(self, otp):
        if not self.otp_secret:
            return False
        totp = pyotp.TOTP(self.otp_secret)
        return totp.verify(otp)
    
    def set_password(self, raw_password):
        self.password = cipher_suite.encrypt(raw_password.encode()).decode()
        self.save()
    
    def check_password(self, raw_password):
        try:
            decrypted_password = cipher_suite.decrypt(self.password.encode()).decode()
            return decrypted_password == raw_password
        except:
            return False

    def __str__(self):
        return self.email
