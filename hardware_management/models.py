from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    is_first_login = models.BooleanField(default=True)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_employees')
    phone = models.CharField(max_length=15, blank=True, null=True)

class Project(models.Model):
    project_id = models.CharField(max_length=50, unique=True)
    project_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=200)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.project_id} - {self.project_name}"

class HardwareType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class Hardware(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('retired', 'Retired'),
    )
    
    hardware_type = models.ForeignKey(HardwareType, on_delete=models.CASCADE)
    serial_number = models.CharField(max_length=100, unique=True)
    model_name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100, blank=True, null=True)
    specifications = models.TextField(blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.hardware_type.name} - {self.serial_number}"

class HardwareAssignment(models.Model):
    assignment_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='hardware_assignments')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='hardware_assignments')
    hardware_items = models.ManyToManyField(Hardware, through='HardwareAssignmentItem')
    exam_city = models.CharField(max_length=200, blank=True, null=True, help_text="City where the employee will take the exam")
    assigned_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assignments_made')
    assigned_date = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Assignment {self.assignment_id} - {self.employee.username}"

class HardwareAssignmentItem(models.Model):
    assignment = models.ForeignKey(HardwareAssignment, on_delete=models.CASCADE)
    hardware = models.ForeignKey(Hardware, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    condition_at_assignment = models.TextField(blank=True, null=True)
    condition_at_return = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('assignment', 'hardware')

class HardwareSerialEntry(models.Model):
    assignment_item = models.OneToOneField(HardwareAssignmentItem, on_delete=models.CASCADE, related_name='serial_entry')
    serial_number = models.CharField(max_length=100)
    entered_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    entered_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_entries')
    verified_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Serial: {self.serial_number}"
    

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import random

User = get_user_model()

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    def __str__(self):
        return f"OTP for {self.user.username}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @classmethod
    def generate_otp(cls, user):
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        expires_at = timezone.now() + timezone.timedelta(seconds=300)  # 5 minutes
        
        # Invalidate any existing OTPs for this user
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Create new OTP
        return cls.objects.create(
            user=user,
            otp=otp,
            expires_at=expires_at
        )
    
    class Meta:
        ordering = ['-created_at']    