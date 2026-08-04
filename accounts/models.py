from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('EXAM_CONTROLLER', 'Examination Controller'),
        ('FACULTY', 'Faculty'),
        ('STUDENT', 'Student'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT')
    email_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, default='')
    address = models.TextField(blank=True, default='')


    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'ADMIN' or self.is_superuser

    @property
    def is_exam_controller(self):
        return self.role == 'EXAM_CONTROLLER' or self.role == 'ADMIN' or self.is_superuser

    @property
    def is_faculty(self):
        return self.role == 'FACULTY'

    @property
    def is_student(self):
        return self.role == 'STUDENT'

    @property
    def avatar_url(self):
        if self.is_student:
            try:
                if self.student_profile.photo:
                    return self.student_profile.photo.url
            except Exception:
                pass
        elif self.is_faculty:
            try:
                if self.faculty_profile.photo:
                    return self.faculty_profile.photo.url
            except Exception:
                pass
        if self.profile_picture:
            return self.profile_picture.url
        return f"https://api.dicebear.com/7.x/adventurer/svg?seed={self.username}"

