from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
import django.utils.timezone

from .models import Student, Assignment, AssignmentSubmission
from .forms import StudentForm, StudentUserForm, SubmissionForm, StudentProfileEditForm
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
        
    gpa = student.semester_result_gpa
    if gpa >= 9.0:
        standing = 'Excellent (First Class Distinction)'
        gpa_class = 'text-success'
    elif gpa >= 7.5:
        standing = 'Very Good (First Class)'
        gpa_class = 'text-info'
    elif gpa >= 5.0:
        standing = 'Good (Second Class)'
        gpa_class = 'text-warning'
    else:
        standing = 'Needs Improvement / Fail'
        gpa_class = 'text-danger'
        
    return render(request, 'students/results.html', {
        'student_profile': student,
        'standing': standing,
        'gpa_class': gpa_class
    })
