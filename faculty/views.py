from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count

from .models import Faculty
from .forms import FacultyForm, FacultyUserForm, FacultyProfileEditForm
from accounts.models import User
from departments.models import Department
from students.models import Student, Assignment, AssignmentSubmission, ExamMark, ExamPublishControl
from students.forms import AssignmentForm, GradeForm, ExamMarkForm

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
        faculty_form = FacultyForm(request.POST, request.FILES)
        
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
        faculty_form = FacultyForm(request.POST, request.FILES, instance=faculty)
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
def faculty_id_card(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    return render(request, 'faculty/id_card.html', {'faculty_profile': faculty})

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
        form = FacultyProfileEditForm(request.POST, request.FILES, instance=faculty)
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


@login_required
def faculty_attendance_manage(request):
    if not request.user.is_faculty:
        messages.error(request, "Permission denied.")
        return redirect('dashboard_home')
        
    try:
        faculty = request.user.faculty_profile
    except Faculty.DoesNotExist:
        messages.error(request, "Faculty profile does not exist.")
        return redirect('dashboard_home')
        
    students = Student.objects.filter(department=faculty.department).order_by('roll_number')
    
    if request.method == 'POST':
        action = request.POST.get('action', '')

        # Quick Single Roll Number Mark
        if action == 'quick_mark':
            quick_roll = request.POST.get('quick_roll_number', '').strip()
            quick_status = request.POST.get('quick_status', 'PRESENT')
            quick_pct = request.POST.get('quick_percentage', '')

            target_student = students.filter(roll_number__iexact=quick_roll).first()
            if target_student:
                if quick_pct:
                    try:
                        val = float(quick_pct)
                        if 0.0 <= val <= 100.0:
                            target_student.attendance_percentage = round(val, 1)
                            target_student.save()
                            messages.success(request, f"Updated Roll No {target_student.roll_number} ({target_student.first_name}) attendance to {val}%.")
                        else:
                            messages.error(request, "Percentage must be between 0 and 100.")
                    except ValueError:
                        messages.error(request, "Invalid percentage value.")
                else:
                    if quick_status == 'PRESENT':
                        target_student.attendance_percentage = min(100.0, round(target_student.attendance_percentage + 2.0, 1))
                        target_student.save()
                        messages.success(request, f"Marked PRESENT for Roll No {target_student.roll_number} ({target_student.first_name} {target_student.last_name}). Attendance: {target_student.attendance_percentage}%.")
                    else:
                        target_student.attendance_percentage = max(0.0, round(target_student.attendance_percentage - 2.0, 1))
                        target_student.save()
                        messages.warning(request, f"Marked ABSENT for Roll No {target_student.roll_number} ({target_student.first_name} {target_student.last_name}). Attendance: {target_student.attendance_percentage}%.")
            else:
                messages.error(request, f"No student found with Roll Number '{quick_roll}' in your department.")

            return redirect('faculty_attendance_manage')

        # Batch Attendance Marking by Roll Number
        for student in students:
            status_key = f'status_{student.id}'
            pct_key = f'attendance_{student.id}'

            # Check if Present/Absent radio was toggled
            if status_key in request.POST:
                mode = request.POST[status_key]
                if mode == 'PRESENT':
                    student.attendance_percentage = min(100.0, round(student.attendance_percentage + 1.5, 1))
                elif mode == 'ABSENT':
                    student.attendance_percentage = max(0.0, round(student.attendance_percentage - 2.5, 1))

            # Direct percentage override
            elif pct_key in request.POST:
                try:
                    val = float(request.POST[pct_key])
                    if 0.0 <= val <= 100.0:
                        student.attendance_percentage = round(val, 1)
                    else:
                        messages.warning(request, f"Skipped invalid value for Roll No {student.roll_number}: {val}%")
                except ValueError:
                    pass

            student.save()

        messages.success(request, "Attendance records updated successfully by Roll Number!")
        return redirect('faculty_attendance_manage')
        
    return render(request, 'faculty/attendance_manage.html', {
        'students': students,
        'faculty': faculty
    })


@login_required
def faculty_results_manage(request):
    if not (request.user.is_exam_controller or request.user.is_faculty or request.user.is_admin):
        messages.error(request, "Permission denied.")
        return redirect('dashboard_home')
        
    faculty = getattr(request.user, 'faculty_profile', None)
    departments = Department.objects.all()
    
    # Selected department filter
    dept_id = request.GET.get('department')
    if dept_id:
        selected_department = Department.objects.filter(pk=dept_id).first()
    elif faculty and faculty.department:
        selected_department = faculty.department
    else:
        selected_department = departments.first()

    # Selected semester filter
    semester_filter = request.GET.get('semester', '')
    query = request.GET.get('q', '')

    all_department_students = Student.objects.filter(department=selected_department).order_by('roll_number') if selected_department else Student.objects.all().order_by('roll_number')
    students = all_department_students

    # Selected student filter
    selected_student_id = request.GET.get('student_id', '')
    if selected_student_id:
        try:
            st_id = int(selected_student_id)
            students = students.filter(pk=st_id)
        except ValueError:
            pass
    
    if query:
        students = students.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(roll_number__icontains=query)
        )

    # Fetch exam marks
    exam_marks = ExamMark.objects.filter(student__in=students).select_related('student').order_by('student', 'semester', 'subject_code')
    if semester_filter:
        try:
            sem_num = int(semester_filter)
            exam_marks = exam_marks.filter(semester=sem_num)
        except ValueError:
            pass

    control = ExamPublishControl.get_control_for(department=selected_department, semester=1)

    if request.method == 'POST':
        action = request.POST.get('action', '')
        
        if action == 'toggle_publish_results':
            if not (request.user.is_exam_controller or request.user.is_admin):
                messages.error(request, "Permission denied. Only Examination Controller or Admin can publish/unpublish semester results.")
                return redirect(request.get_full_path())
            control.results_published = not control.results_published
            control.save()
            st = "PUBLISHED" if control.results_published else "UNPUBLISHED (HELD)"
            messages.success(request, f"Semester Results status set to {st} for {selected_department.name if selected_department else 'All Departments'}.")
            return redirect(request.get_full_path())

        elif action == 'toggle_publish_admit_card':
            if not (request.user.is_exam_controller or request.user.is_admin):
                messages.error(request, "Permission denied. Only Examination Controller or Admin can release/withdraw admit cards.")
                return redirect(request.get_full_path())
            control.admit_card_published = not control.admit_card_published
            control.save()
            st = "RELEASED / PUBLISHED" if control.admit_card_published else "HELD / UNPUBLISHED"
            messages.success(request, f"Exam Admit Cards status set to {st} for {selected_department.name if selected_department else 'All Departments'}.")
            return redirect(request.get_full_path())

        elif action == 'toggle_exam_form_fillup':
            if not (request.user.is_exam_controller or request.user.is_admin):
                messages.error(request, "Permission denied. Only Examination Controller or Admin can open/hold exam registration forms.")
                return redirect(request.get_full_path())
            control.exam_form_open = not control.exam_form_open
            control.save()
            st = "OPEN / ACTIVE" if control.exam_form_open else "HELD / CLOSED"
            messages.success(request, f"Exam Registration Form Fill-Up status set to {st} for {selected_department.name if selected_department else 'All Departments'}.")
            return redirect(request.get_full_path())

        elif action == 'update_exam_info':
            if not (request.user.is_exam_controller or request.user.is_admin):
                messages.error(request, "Permission denied. Only Examination Controller or Admin can change exam settings.")
                return redirect(request.get_full_path())
            control.exam_name = request.POST.get('exam_name', control.exam_name)
            control.exam_center = request.POST.get('exam_center', control.exam_center)
            control.academic_session = request.POST.get('academic_session', control.academic_session)
            control.save()
            messages.success(request, "Exam Controller details updated successfully!")
            return redirect(request.get_full_path())

        elif action == 'add_mark':
            form = ExamMarkForm(request.POST)
            if form.is_valid():
                mark = form.save(commit=False)
                # If faculty member, verify student belongs to their department
                if faculty and not (request.user.is_exam_controller or request.user.is_admin):
                    if mark.student.department != faculty.department:
                        messages.error(request, "Permission denied. You can only enter marks for students in your department.")
                        return redirect(request.get_full_path())
                mark.save()
                messages.success(request, f"Added exam mark for {mark.student.roll_number} - {mark.subject_code}!")
                return redirect(request.get_full_path())
            else:
                messages.error(request, f"Failed to add mark: {form.errors.as_text()}")
                
        elif action == 'edit_mark':
            mark_id = request.POST.get('mark_id')
            mark = get_object_or_404(ExamMark, pk=mark_id)
            if faculty and not (request.user.is_exam_controller or request.user.is_admin):
                if mark.student.department != faculty.department:
                    messages.error(request, "Permission denied. You can only update marks for students in your department.")
                    return redirect(request.get_full_path())
            form = ExamMarkForm(request.POST, instance=mark)
            if form.is_valid():
                form.save()
                messages.success(request, f"Updated marks for {mark.student.roll_number} ({mark.subject_code})!")
                return redirect(request.get_full_path())
            else:
                messages.error(request, f"Failed to update mark: {form.errors.as_text()}")
                
        elif action == 'delete_mark':
            mark_id = request.POST.get('mark_id')
            mark = get_object_or_404(ExamMark, pk=mark_id)
            if faculty and not (request.user.is_exam_controller or request.user.is_admin):
                if mark.student.department != faculty.department:
                    messages.error(request, "Permission denied. You can only delete marks for students in your department.")
                    return redirect(request.get_full_path())
            roll = mark.student.roll_number
            code = mark.subject_code
            mark.delete()
            messages.success(request, f"Deleted exam mark for {roll} - {code}.")
            return redirect(request.get_full_path())

        elif action == 'batch_update':
            for student in students:
                assessment_key = f'assessment_{student.id}'
                if assessment_key in request.POST:
                    student.assessment_status = request.POST[assessment_key]
                    student.save()
            messages.success(request, "Assessment remarks updated successfully!")
            return redirect(request.get_full_path())

    mark_form = ExamMarkForm()
    
    student_summaries = []
    for st in students:
        student_summaries.append({
            'student': st,
            'cgpa': st.get_cgpa(),
            'total_credits': st.get_total_credits(),
            'semester_results': st.get_all_semester_results(),
            'marks': exam_marks.filter(student=st)
        })

    return render(request, 'faculty/results_manage.html', {
        'students': students,
        'all_department_students': all_department_students,
        'selected_student_id': selected_student_id,
        'student_summaries': student_summaries,
        'exam_marks': exam_marks,
        'mark_form': mark_form,
        'faculty': faculty,
        'departments': departments,
        'selected_department': selected_department,
        'selected_semester': semester_filter,
        'query': query,
        'control': control,
    })

@login_required
def add_exam_mark(request):
    if not (request.user.is_exam_controller or request.user.is_faculty or request.user.is_admin):
        messages.error(request, "Permission denied.")
        return redirect('dashboard_home')
        
    if request.method == 'POST':
        form = ExamMarkForm(request.POST)
        if form.is_valid():
            mark = form.save()
            messages.success(request, f"Exam mark added successfully for {mark.student.roll_number} ({mark.subject_code}).")
            return redirect('faculty_results_manage')
        else:
            messages.error(request, f"Failed to save exam mark: {form.errors.as_text()}")
    else:
        form = ExamMarkForm()
        
    return render(request, 'faculty/add_exam_mark.html', {'form': form})

@login_required
def edit_exam_mark(request, pk):
    if not (request.user.is_exam_controller or request.user.is_faculty or request.user.is_admin):
        messages.error(request, "Permission denied.")
        return redirect('dashboard_home')
        
    mark = get_object_or_404(ExamMark, pk=pk)
    if request.method == 'POST':
        form = ExamMarkForm(request.POST, instance=mark)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated exam mark for {mark.student.roll_number} - {mark.subject_code}.")
            return redirect('faculty_results_manage')
        else:
            messages.error(request, f"Failed to update exam mark: {form.errors.as_text()}")
    else:
        form = ExamMarkForm(instance=mark)
        
    return render(request, 'faculty/edit_exam_mark.html', {'form': form, 'mark': mark})

@login_required
def delete_exam_mark(request, pk):
    if not (request.user.is_exam_controller or request.user.is_faculty or request.user.is_admin):
        messages.error(request, "Permission denied.")
        return redirect('dashboard_home')
        
    mark = get_object_or_404(ExamMark, pk=pk)
    student_name = f"{mark.student.first_name} {mark.student.last_name}"
    subject_code = mark.subject_code
    mark.delete()
    messages.success(request, f"Deleted {subject_code} exam mark for {student_name}.")
    return redirect('faculty_results_manage')

@login_required
def faculty_classroom_alerts(request):
    return redirect('classroom_alert_list')

@login_required
def faculty_timetable(request):
    return redirect('timetable_view')

from students.models import ExamFormRegistration

@login_required
def faculty_exam_forms_manage(request):
    if not (request.user.is_exam_controller or request.user.is_faculty or request.user.is_admin):
        messages.error(request, "Permission denied.")
        return redirect('dashboard_home')

    semester_filter = request.GET.get('semester', '')
    status_filter = request.GET.get('status', '').strip()
    query = request.GET.get('q', '').strip()

    exam_forms = ExamFormRegistration.objects.select_related('student').all().order_by('-submitted_at')

    if semester_filter:
        try:
            sem_num = int(semester_filter)
            exam_forms = exam_forms.filter(semester=sem_num)
        except ValueError:
            pass

    if status_filter:
        exam_forms = exam_forms.filter(status=status_filter)

    if query:
        exam_forms = exam_forms.filter(
            Q(student__first_name__icontains=query) |
            Q(student__last_name__icontains=query) |
            Q(student__roll_number__icontains=query)
        )

    if request.method == 'POST':
        action = request.POST.get('action', '')
        form_id = request.POST.get('form_id')
        exam_form = get_object_or_404(ExamFormRegistration, pk=form_id)

        if action == 'approve':
            exam_form.status = 'APPROVED'
            exam_form.save()
            messages.success(request, f"Approved Examination Form #{exam_form.id} for student {exam_form.student.roll_number} ({exam_form.student.first_name})!")
        elif action == 'reject':
            exam_form.status = 'REJECTED'
            exam_form.remarks = request.POST.get('remarks', 'Rejected by Examination Controller.')
            exam_form.save()
            messages.warning(request, f"Rejected Examination Form #{exam_form.id} for student {exam_form.student.roll_number}.")
        elif action == 'delete':
            exam_form.delete()
            messages.success(request, f"Deleted Examination Form record #{form_id}.")

        return redirect(request.get_full_path())

    return render(request, 'faculty/exam_forms_manage.html', {
        'exam_forms': exam_forms,
        'selected_semester': semester_filter,
        'selected_status': status_filter,
        'query': query,
    })


@login_required
def update_student_phone(request, pk):
    if not (request.user.is_admin or request.user.is_faculty or request.user.is_exam_controller):
        messages.error(request, "Permission denied.")
        return redirect('dashboard_home')

    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        phone = request.POST.get('phone_number', '').strip()
        student.phone_number = phone
        student.save()
        messages.success(request, f"Successfully updated contact phone number for {student.first_name} {student.last_name} ({student.roll_number}) to '{phone}'!")

    next_url = request.META.get('HTTP_REFERER') or 'dashboard_home'
    return redirect(next_url)



