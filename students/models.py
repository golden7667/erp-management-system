from django.db import models
from django.conf import settings
from departments.models import Department

class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile', db_constraint=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    roll_number = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='students', db_constraint=False)
    photo = models.ImageField(upload_to='students/', blank=True, null=True)
    attendance_percentage = models.FloatField(default=85.0)
    semester_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=15000.00)
    semester_fee_status = models.CharField(max_length=20, choices=[('PAID', 'Paid'), ('PENDING', 'Pending'), ('OVERDUE', 'Overdue')], default='PAID')
    semester_result_gpa = models.FloatField(default=3.80)
    assessment_status = models.CharField(max_length=100, default='All Cleared (Internal Assessments)')
    phone_number = models.CharField(max_length=15, blank=True, default='')
    address = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.roll_number})"


from faculty.models import Faculty

class Assignment(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateTimeField()
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='assignments', db_constraint=False)
    created_by = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='assignments', db_constraint=False)
    created_at = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to='assignments/', blank=True, null=True)

    def __str__(self):
        return self.title

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions')
    submitted_file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.CharField(max_length=10, blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student} - {self.assignment}"
