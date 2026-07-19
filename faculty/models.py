from django.db import models
from django.conf import settings
from departments.models import Department

class Faculty(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='faculty_profile', db_constraint=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='faculty', db_constraint=False)
    subject = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True, default='')
    office_location = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return f"Prof. {self.first_name} {self.last_name} ({self.employee_id})"
