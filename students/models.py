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

    def get_semester_gpa(self, semester):
        marks = self.exam_marks.filter(semester=semester)
        if not marks.exists():
            return 0.0
        total_points = sum(m.grade_point * m.credits for m in marks)
        total_credits = sum(m.credits for m in marks)
        if total_credits == 0:
            return 0.0
        return round(total_points / total_credits, 2)

    def get_cgpa(self):
        marks = self.exam_marks.all()
        if not marks.exists():
            return self.semester_result_gpa or 0.0
        total_points = sum(m.grade_point * m.credits for m in marks)
        total_credits = sum(m.credits for m in marks)
        if total_credits == 0:
            return 0.0
        return round(total_points / total_credits, 2)

    def get_total_credits(self):
        marks = self.exam_marks.all()
        return sum(m.credits for m in marks)

    def get_all_semester_results(self):
        semesters = self.exam_marks.values_list('semester', flat=True).distinct().order_by('semester')
        results = []
        for sem in semesters:
            marks = self.exam_marks.filter(semester=sem)
            gpa = self.get_semester_gpa(sem)
            total_credits = sum(m.credits for m in marks)
            results.append({
                'semester': sem,
                'marks': marks,
                'gpa': gpa,
                'total_credits': total_credits
            })
        return results

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


class ExamMark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_marks')
    semester = models.IntegerField(default=1)
    subject_code = models.CharField(max_length=20)
    subject_name = models.CharField(max_length=100)
    credits = models.IntegerField(default=4)
    internal_marks = models.FloatField(default=25.0, help_text="Max 30 Marks")
    mid_sem_marks = models.FloatField(default=25.0, help_text="Max 30 Marks")
    final_sem_marks = models.FloatField(default=35.0, help_text="Max 40 Marks")

    class Meta:
        unique_together = ('student', 'semester', 'subject_code')
        ordering = ['semester', 'subject_code']

    @property
    def total_marks(self):
        return round(self.internal_marks + self.mid_sem_marks + self.final_sem_marks, 2)

    @property
    def grade_point(self):
        tot = self.total_marks
        if tot >= 90:
            return 10.0
        elif tot >= 80:
            return 9.0
        elif tot >= 70:
            return 8.0
        elif tot >= 60:
            return 7.0
        elif tot >= 50:
            return 6.0
        elif tot >= 40:
            return 5.0
        else:
            return 0.0

    @property
    def letter_grade(self):
        gp = self.grade_point
        if gp == 10.0:
            return 'O'
        elif gp == 9.0:
            return 'A+'
        elif gp == 8.0:
            return 'A'
        elif gp == 7.0:
            return 'B+'
        elif gp == 6.0:
            return 'B'
        elif gp == 5.0:
            return 'C'
        else:
            return 'F'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.student_id:
            cgpa = self.student.get_cgpa()
            if self.student.semester_result_gpa != cgpa:
                self.student.semester_result_gpa = cgpa
                self.student.save(update_fields=['semester_result_gpa'])

    def delete(self, *args, **kwargs):
        student = self.student
        super().delete(*args, **kwargs)
        if student:
            cgpa = student.get_cgpa()
            if student.semester_result_gpa != cgpa:
                student.semester_result_gpa = cgpa
                student.save(update_fields=['semester_result_gpa'])

    def __str__(self):
        return f"{self.student.roll_number} - Sem {self.semester} - {self.subject_code} ({self.total_marks}/100)"


class ExamPublishControl(models.Model):
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='exam_publish_controls', db_constraint=False)
    semester = models.IntegerField(default=1)
    results_published = models.BooleanField(default=True, help_text="Publish Semester Results to Students")
    admit_card_published = models.BooleanField(default=True, help_text="Release Exam Admit Cards to Students")
    exam_form_open = models.BooleanField(default=True, help_text="Open Examination Application Form Fill-Up to Students")
    exam_name = models.CharField(max_length=150, default="End-Semester Theory Examinations - August 2026")
    academic_session = models.CharField(max_length=50, default="2026-2027")
    exam_center = models.CharField(max_length=150, default="Smart College Main Campus, Examination Block-A")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['department', 'semester']

    @classmethod
    def get_control_for(cls, department=None, semester=1):
        control, _ = cls.objects.get_or_create(
            department=department,
            semester=semester,
            defaults={
                'results_published': True,
                'admit_card_published': True,
                'exam_form_open': True,
                'exam_name': 'End-Semester Theory Examinations - August 2026',
                'academic_session': '2026-2027',
                'exam_center': 'Smart College Main Campus, Examination Block-A'
            }
        )
        return control

    def __str__(self):
        dept_str = self.department.code if self.department else "All Departments"
        return f"Exam Control - {dept_str} (Sem {self.semester}): Results={self.results_published}, AdmitCard={self.admit_card_published}"


class ExamFormRegistration(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Submitted - Pending Verification'),
        ('APPROVED', 'Approved by Exam Controller'),
        ('REJECTED', 'Rejected / Needs Revision'),
    ]

    EXAM_TYPE_CHOICES = [
        ('REGULAR', 'Regular Semester Examination'),
        ('BACKLOG', 'Backlog / Re-appear Examination'),
        ('SPECIAL', 'Special / Supplementary Examination'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_form_registrations')
    academic_session = models.CharField(max_length=30, default='2026-2027')
    semester = models.IntegerField(default=1)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES, default='REGULAR')
    subjects_list = models.TextField(help_text="Comma-separated subject codes/names")
    fee_paid = models.BooleanField(default=True, help_text="Exam Registration Fee Status")
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2, default=1200.00)
    transaction_id = models.CharField(max_length=50, blank=True, default='TXN-ERP-202608')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='APPROVED')
    remarks = models.TextField(blank=True, default='')
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Exam Form #{self.id} - {self.student.roll_number} (Sem {self.semester}) [{self.get_status_display()}]"




