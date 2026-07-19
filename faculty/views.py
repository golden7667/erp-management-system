from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count

from .models import Faculty
from .forms import FacultyForm, FacultyUserForm, FacultyProfileEditForm
from accounts.models import User
from students.models import Assignment, AssignmentSubmission
from students.forms import AssignmentForm, GradeForm

@login_required
def faculty_list(request):
    if not (request.user.is_admin or request.user.is_faculty):
        messages.error(request, "Permission denied.")
        return redirect('dashboard_home')
        
    query = request.GET.get('q', '')
    faculties = Faculty.objects.prefetch_related('department', 'user').all()
    
    if query:
        faculties = faculties.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(employee_id__icontains=query) |
            Q(subject__icontains=query)
        )
        
    return render(request, 'faculty/list.html', {'faculties': faculties, 'query': query})

@login_required
def faculty_add(request):
    if not request.user.is_admin:
        messages.error(request, "Permission denied.")
        return redirect('faculty_list')
        
    if request.method == 'POST':
        user_form = FacultyUserForm(request.POST)
        faculty_form = FacultyForm(request.POST)
        
        if user_form.is_valid() and faculty_form.is_valid():
            # Create user
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.role = 'FACULTY'
            user.save()
            
            # Create faculty profile
            faculty = faculty_form.save(commit=False)
            faculty.user = user
            faculty.save()
            
            messages.success(request, f"Faculty {faculty} registered successfully!")
            return redirect('faculty_list')
    else:
        user_form = FacultyUserForm()
        faculty_form = FacultyForm()
        
    return render(request, 'faculty/add.html', {
        'user_form': user_form,
        'faculty_form': faculty_form
    })

@login_required
def faculty_edit(request, pk):
    if not request.user.is_admin:
        messages.error(request, "Permission denied.")
        return redirect('faculty_list')
        
    faculty = get_object_or_404(Faculty, pk=pk)
    
    if request.method == 'POST':
        faculty_form = FacultyForm(request.POST, instance=faculty)
        if faculty_form.is_valid():
            faculty_form.save()
            messages.success(request, f"Faculty {faculty} updated successfully!")
            return redirect('faculty_list')
    else:
        faculty_form = FacultyForm(instance=faculty)
        
    return render(request, 'faculty/edit.html', {
        'faculty_form': faculty_form,
        'faculty': faculty
    })

@login_required
def faculty_delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, "Permission denied.")
        return redirect('faculty_list')
        
    faculty = get_object_or_404(Faculty, pk=pk)
    user = faculty.user
    faculty.delete()
    user.delete()
    messages.success(request, "Faculty profile deleted successfully.")
    return redirect('faculty_list')

@login_required
def faculty_assignments(request):
    if not request.user.is_faculty:
        messages.error(request, "Permission denied.")
        return redirect('dashboard_home')
        
    faculty = request.user.faculty_profile
    assignments = Assignment.objects.filter(created_by=faculty).annotate(submission_count=Count('submissions')).order_by('-created_at')
    
    return render(request, 'faculty/assignments.html', {
        'assignments': assignments
    })

@login_required
def add_assignment(request):
    if not request.user.is_faculty:
        messages.error(request, "Permission denied.")
        return redirect('dashboard_home')
        
    faculty = request.user.faculty_profile
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = faculty
            assignment.save()
            messages.success(request, f"Assignment '{assignment.title}' created successfully!")
            return redirect('faculty_assignments')
    else:
        form = AssignmentForm(initial={'department': faculty.department})
        
    return render(request, 'faculty/add_assignment.html', {'form': form})

@login_required
def view_submissions(request, pk):
    if not request.user.is_faculty:
        messages.error(request, "Permission denied.")
        return redirect('dashboard_home')
        
    faculty = request.user.faculty_profile
    assignment = get_object_or_404(Assignment, pk=pk, created_by=faculty)
    submissions = assignment.submissions.prefetch_related('student').all()
    
    return render(request, 'faculty/view_submissions.html', {
        'assignment': assignment,
        'submissions': submissions
    })

@login_required
def grade_submission(request, submission_id):
    if not request.user.is_faculty:
        messages.error(request, "Permission denied.")
        return redirect('dashboard_home')
        
    faculty = request.user.faculty_profile
    submission = get_object_or_404(AssignmentSubmission, pk=submission_id, assignment__created_by=faculty)
    
    if request.method == 'POST':
        form = GradeForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, f"Submission for {submission.student} has been graded!")
            return redirect('view_submissions', pk=submission.assignment.id)
    else:
        form = GradeForm(instance=submission)
        
    return render(request, 'faculty/grade_submission.html', {
        'submission': submission,
        'form': form
    })

@login_required
def faculty_profile_edit(request):
    if not request.user.is_faculty:
        messages.error(request, "Permission denied.")
        return redirect('dashboard_home')
        
    try:
        faculty = request.user.faculty_profile
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile does not exist.")
        return redirect('dashboard_home')
        
    if request.method == 'POST':
        form = FacultyProfileEditForm(request.POST, instance=faculty)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('dashboard_home')
    else:
        form = FacultyProfileEditForm(instance=faculty)
        
    return render(request, 'faculty/profile_edit.html', {
        'form': form,
        'faculty': faculty
    })
