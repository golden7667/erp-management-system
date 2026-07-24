from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class ClassroomAlert(models.Model):
    ALERT_TYPE_CHOICES = [
        ('ROOM_CHANGE', 'Room Change'),
        ('CANCELLATION', 'Class Cancelled'),
        ('SCHEDULE_CHANGE', 'Schedule Shift'),
        ('URGENT', 'Urgent Notice'),
        ('INFO', 'General Info'),
    ]

    PRIORITY_CHOICES = [
        ('HIGH', 'High / Urgent'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]

    title = models.CharField(max_length=150)
    room_number = models.CharField(max_length=50, help_text="e.g. Room 302, LH-01")
    subject = models.CharField(max_length=100, blank=True, default='')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES, default='INFO')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    message = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='classroom_alerts', db_constraint=False)
    created_by_faculty = models.ForeignKey('faculty.Faculty', on_delete=models.SET_NULL, null=True, blank=True, related_name='classroom_alerts', db_constraint=False)
    created_by_name = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_alert_type_display()}] {self.title} - {self.room_number}"


class TimetableSlot(models.Model):
    DAY_CHOICES = [
        ('MONDAY', 'Monday'),
        ('TUESDAY', 'Tuesday'),
        ('WEDNESDAY', 'Wednesday'),
        ('THURSDAY', 'Thursday'),
        ('FRIDAY', 'Friday'),
        ('SATURDAY', 'Saturday'),
    ]

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='timetable_slots', db_constraint=False)
    subject = models.CharField(max_length=100)
    faculty = models.ForeignKey('faculty.Faculty', on_delete=models.SET_NULL, null=True, blank=True, related_name='timetable_slots', db_constraint=False)
    day_of_week = models.CharField(max_length=15, choices=DAY_CHOICES, default='MONDAY')
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_number = models.CharField(max_length=50, default='Room 101')
    semester_or_year = models.CharField(max_length=50, default='Semester 1', blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.department.code} | {self.day_of_week} | {self.subject} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"
