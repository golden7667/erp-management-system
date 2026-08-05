from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
import django.utils.timezone

from .models import Student, Assignment, AssignmentSubmission, ExamMark, ExamPublishControl
from .forms import StudentForm, StudentUserForm, SubmissionForm, StudentProfileEditForm, ExamMarkForm
from accounts.models import User

@login_required
def student_list(request):
    if not (request.user.is_admin or request.user.is_faculty):
        messages.error(request, "Permission denied.")
        return redirect('dashboard_home')
        
    query = request.GET.get('q', '')
    students = Student.objects.prefetch_related('department', 'user').all()
    
    if query:
        students = students.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(roll_number__icontains=query)
        )
        
    return render(request, 'students/list.html', {'students': students, 'query': query})

@login_required
def student_add(request):
    if not request.user.is_admin:
        messages.error(request, "Permission denied.")
        return redirect('student_list')
        
    if request.method == 'POST':
        user_form = StudentUserForm(request.POST)
        student_form = StudentForm(request.POST, request.FILES)
        
        if user_form.is_valid() and student_form.is_valid():
            # Create user first
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.role = 'STUDENT'
            user.save()
            
            # Create student profile
            student = student_form.save(commit=False)
            student.user = user
            student.save()
            
            messages.success(request, f"Student {student} registered successfully!")
            return redirect('student_list')
    else:
        user_form = StudentUserForm()
        student_form = StudentForm()
        
    return render(request, 'students/add.html', {
        'user_form': user_form,
        'student_form': student_form
    })

@login_required
def student_edit(request, pk):
    if not request.user.is_admin:
        messages.error(request, "Permission denied.")
        return redirect('student_list')
        
    student = get_object_or_404(Student, pk=pk)
    user = student.user
    
    if request.method == 'POST':
        student_form = StudentForm(request.POST, request.FILES, instance=student)
        if student_form.is_valid():
            student_form.save()
            messages.success(request, f"Student {student} updated successfully!")
            return redirect('student_list')
    else:
        student_form = StudentForm(instance=student)
        
    return render(request, 'students/edit.html', {
        'student_form': student_form,
        'student': student
    })

@login_required
def student_delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, "Permission denied.")
        return redirect('student_list')
        
    student = get_object_or_404(Student, pk=pk)
    user = student.user
    student.delete()
    user.delete()
    messages.success(request, "Student profile deleted successfully.")
    return redirect('student_list')

@login_required
def student_id_card(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'students/id_card.html', {'student_profile': student})

@login_required
def student_assignments(request):
    if not request.user.is_student:
        messages.error(request, "Permission denied.")
        return redirect('dashboard_home')
        
    student = request.user.student_profile
    assignments = Assignment.objects.filter(department=student.department).order_by('-created_at')
    
    # Fetch submissions by this student
    submissions = {s.assignment_id: s for s in student.submissions.all()}
    
    # Build a list of assignments with submission context
    assignments_with_status = []
    for a in assignments:
        sub = submissions.get(a.id)
        assignments_with_status.append({
            'assignment': a,
            'submission': sub,
            'is_overdue': a.due_date < django.utils.timezone.now() and not sub
        })
        
    return render(request, 'students/assignments.html', {
        'assignments': assignments_with_status
    })

@login_required
def submit_assignment(request, pk):
    if not request.user.is_student:
        messages.error(request, "Permission denied.")
        return redirect('dashboard_home')
        
    student = request.user.student_profile
    assignment = get_object_or_404(Assignment, pk=pk, department=student.department)
    
    # Check if already submitted
    submission = AssignmentSubmission.objects.filter(assignment=assignment, student=student).first()
    
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            new_sub = form.save(commit=False)
            new_sub.assignment = assignment
            new_sub.student = student
            new_sub.save()
            messages.success(request, f"Assignment '{assignment.title}' submitted successfully!")
            return redirect('student_assignments')
    else:
        form = SubmissionForm(instance=submission)
        
    return render(request, 'students/submit_assignment.html', {
        'assignment': assignment,
        'form': form,
        'submission': submission
    })

@login_required
def student_profile_edit(request):
    if not request.user.is_student:
        messages.error(request, "Permission denied.")
        return redirect('dashboard_home')
        
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, "Student profile does not exist.")
        return redirect('dashboard_home')
        
    if request.method == 'POST':
        form = StudentProfileEditForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('dashboard_home')
    else:
        form = StudentProfileEditForm(instance=student)
        
    return render(request, 'students/profile_edit.html', {
        'form': form,
        'student': student
    })

@login_required
def student_results(request):
    if not request.user.is_student:
        messages.error(request, "Permission denied.")
        return redirect('dashboard_home')
        
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, "Student profile does not exist.")
        return redirect('dashboard_home')
        
    # Check Exam Controller publish status
    control = ExamPublishControl.get_control_for(department=student.department, semester=1)
    results_published = control.results_published if control else True

    cgpa = student.get_cgpa()
    semester_results = student.get_all_semester_results()
    total_credits = student.get_total_credits()
    latest_gpa = semester_results[-1]['gpa'] if semester_results else cgpa
    
    if cgpa >= 9.0:
        standing = 'Outstanding (First Class Distinction)'
        gpa_class = 'text-success'
    elif cgpa >= 7.5:
        standing = 'Very Good (First Class)'
        gpa_class = 'text-info'
    elif cgpa >= 5.0:
        standing = 'Good (Second Class)'
        gpa_class = 'text-warning'
    else:
        standing = 'Needs Improvement / Fail'
        gpa_class = 'text-danger'
        
    return render(request, 'students/results.html', {
        'student_profile': student,
        'cgpa': cgpa,
        'latest_gpa': latest_gpa,
        'total_credits': total_credits,
        'semester_results': semester_results,
        'standing': standing,
        'gpa_class': gpa_class,
        'results_published': results_published,
        'control': control,
    })

@login_required
def student_classroom_alerts(request):
    return redirect('classroom_alert_list')

@login_required
def student_timetable(request):
    return redirect('timetable_view')

@login_required
def student_admit_card(request, pk=None):
    all_students = None
    student = None

    if request.user.is_admin or request.user.is_exam_controller or request.user.is_faculty:
        all_students = Student.objects.prefetch_related('department').all().order_by('roll_number')
        if request.user.is_faculty and not (request.user.is_admin or request.user.is_exam_controller):
            faculty = getattr(request.user, 'faculty_profile', None)
            if faculty and faculty.department:
                all_students = all_students.filter(department=faculty.department)
        student_id = request.GET.get('student_id') or pk
        if student_id:
            student = get_object_or_404(Student, pk=student_id)
        else:
            student = all_students.first()
        admit_card_published = True
        control = ExamPublishControl.get_control_for(department=student.department if student else None, semester=1)
    else:
        # Student user
        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            messages.error(request, "No student profile found for your account.")
            return redirect('dashboard_home')

        control = ExamPublishControl.get_control_for(department=student.department, semester=1)
        admit_card_published = control.admit_card_published if control else True

    if not student:
        messages.error(request, "No student profile found for Admit Card.")
        return redirect('dashboard_home')

    exam_schedule = [
        {'code': 'CS-501', 'subject': 'Data Structures & Algorithms', 'date': 'Aug 12, 2026', 'time': '10:00 AM - 01:00 PM', 'room': 'Lab-102'},
        {'code': 'CS-502', 'subject': 'Database Management Systems', 'date': 'Aug 14, 2026', 'time': '10:00 AM - 01:00 PM', 'room': 'Hall-A'},
        {'code': 'CS-503', 'subject': 'Computer Networks & Security', 'date': 'Aug 17, 2026', 'time': '10:00 AM - 01:00 PM', 'room': 'Hall-B'},
        {'code': 'CS-504', 'subject': 'Software Engineering & Agile', 'date': 'Aug 19, 2026', 'time': '10:00 AM - 01:00 PM', 'room': 'Lab-105'},
        {'code': 'CS-505', 'subject': 'Web Technologies & Frameworks', 'date': 'Aug 21, 2026', 'time': '10:00 AM - 01:00 PM', 'room': 'Hall-C'},
    ]

    return render(request, 'students/admit_card.html', {
        'student_profile': student,
        'all_students': all_students,
        'exam_schedule': exam_schedule,
        'exam_name': control.exam_name if control else 'End-Semester Theory Examinations - August 2026',
        'exam_center': control.exam_center if control else 'Smart College Main Campus, Examination Block-A',
        'admit_card_published': admit_card_published,
        'control': control,
    })

from .models import ExamFormRegistration

@login_required
def student_exam_form(request):
    if not request.user.is_student:
        messages.error(request, "Permission denied. Only students can access the Examination Registration Form.")
        return redirect('dashboard_home')

    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, "No student profile found for your account.")
        return redirect('dashboard_home')

    existing_forms = ExamFormRegistration.objects.filter(student=student)
    latest_form = existing_forms.first()

    default_subjects = [
        "CS-501: Data Structures & Algorithms",
        "CS-502: Database Management Systems",
        "CS-503: Computer Networks & Security",
        "CS-504: Software Engineering & Agile",
        "CS-505: Web Technologies & Frameworks"
    ]

    if request.method == 'POST':
        semester = request.POST.get('semester', 1)
        exam_type = request.POST.get('exam_type', 'REGULAR')
        academic_session = request.POST.get('academic_session', '2026-2027')
        selected_subjects = request.POST.getlist('subjects')
        custom_subjects = request.POST.get('custom_subjects', '').strip()

        all_subjects_str = ", ".join(selected_subjects)
        if custom_subjects:
            all_subjects_str = f"{all_subjects_str}, {custom_subjects}" if all_subjects_str else custom_subjects

        if not all_subjects_str:
            all_subjects_str = ", ".join(default_subjects)

        form_entry = ExamFormRegistration.objects.create(
            student=student,
            semester=semester,
            exam_type=exam_type,
            academic_session=academic_session,
            subjects_list=all_subjects_str,
            fee_paid=True,
            amount_paid=1200.00,
            transaction_id=f"TXN-ERP-{student.roll_number}-2026",
            status='APPROVED',
        )

        messages.success(request, f"Examination Registration Form #{form_entry.id} submitted successfully! Your Admit Card is now available for download.")
        return redirect('student_exam_form')

    return render(request, 'students/exam_form.html', {
        'student_profile': student,
        'existing_forms': existing_forms,
        'latest_form': latest_form,
        'default_subjects': default_subjects,
    })


