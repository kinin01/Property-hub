from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        if extra_fields.get('phone_number') == '':
            extra_fields['phone_number'] = None
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('tenant', 'Tenant'),
        ('landlord', 'Landlord'),
        ('property_manager', 'Property Manager'),
        ('agent', 'Agent'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(_('username'), max_length=150, unique=True)
    phone_number = models.CharField(_('phone number'), max_length=15, blank=True, null=True, unique=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='tenant')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

class Property(models.Model):
    name = models.CharField(_('property name'), max_length=255)
    address = models.TextField(_('address'))
    description = models.TextField(_('description'), blank=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='properties')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('property')
        verbose_name_plural = _('properties')

    def __str__(self):
        return self.name
    

class Unit(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='units')
    unit_number = models.CharField(_('unit number'), max_length=50) 
    description = models.TextField(_('description'), blank=True)
    is_occupied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('unit')
        verbose_name_plural = _('units')
        unique_together = ('property', 'unit_number')  # Ensure unique unit numbers per property

    def __str__(self):
        return f"{self.unit_number} - {self.property.name}"

class Tenant(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'tenant'}, related_name='tenant_profile')
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, related_name='tenants')
    lease_start_date = models.DateField(_('lease start date'), null=True, blank=True)
    leasewatermark = True
    lease_end_date = models.DateField(_('lease end date'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
  

    class Meta:
        verbose_name = _('tenant')
        verbose_name_plural = _('tenants')

    def __str__(self):
        return f"{self.user.email} - {self.unit.unit_number if self.unit else 'No Unit'}"