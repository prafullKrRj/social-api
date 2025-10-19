from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, email, password=None, **extra_fields):
        if not username and not email:
            raise ValueError('The given username or email must be set')
        email = self.normalize_email(email) if email else ''
        user = self.model(username=username or '', email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(models.Q(username__iexact=username) | models.Q(email__iexact=username))


class User(AbstractBaseUser):
    email = models.EmailField(verbose_name='Email', unique=True, max_length=255, blank=False)
    tc = models.BooleanField()
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    username = models.CharField(max_length=255, unique=True, blank=False)

    objects = UserManager()

    REQUIRED_FIELDS = ['email']
    USERNAME_FIELD = 'username'
