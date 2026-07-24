from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Department, ClassroomAlert, TimetableSlot
from .forms import ClassroomAlertForm, TimetableSlotForm
from faculty.models import Faculty
from students.models import Student

@login_required
def department_list(request):
    if not (request.user.is_admin or request.user.is_faculty):
        messages.error(request, "Permission denied.")
        return redirect('dashboard_home')
    departments = Department.objects.all()
    return render(request, 'departments/list.html', {'departments': departments})

@login_required
def department_add(request):
    if not request.user.is_admin:
        messages.error(request, "Permission denied.")
        return redirect('department_list')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        description = request.POST.get('description', '')
        
        if not name or not code:
            messages.error(request, "Name and code are required.")
        elif Department.objects.filter(code=code).exists():
            messages.error(request, "A department with this code already exists.")
        else:
            Department.objects.create(name=name, code=code.upper(), description=description)
            messages.success(request, f"Department '{name}' created successfully!")
            return redirect('department_list')
            
    return render(request, 'departments/add.html')

@login_required
def department_edit(request, pk):
    if not request.user.is_admin:
        messages.error(request, "Permission denied.")
        return redirect('department_list')
        
    dept = get_object_or_404(Department, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        description = request.POST.get('description', '')
        
        if not name or not code:
            messages.error(request, "Name and code are required.")
        elif Department.objects.filter(code=code).exclude(pk=pk).exists():
            messages.error(request, "A department with this code already exists.")
        else:
            dept.name = name
            dept.code = code.upper()
            dept.description = description
            dept.save()
            messages.success(request, f"Department '{name}' updated successfully!")
            return redirect('department_list')
            
    return render(request, 'departments/edit.html', {'department': dept})

@login_required
def department_delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, "Permission denied.")
        return redirect('department_list')
        
    dept = get_object_or_404(Department, pk=pk)
    dept.delete()
    messages.success(request, "Department deleted successfully.")
    return redirect('department_list')

# --- CLASSROOM ALERTS VIEWS ---

@login_required
def classroom_alert_list(request):
    query = request.GET.get('q', '')
    alert_type_filter = request.GET.get('type', '')
    dept_id = request.GET.get('dept', '')

    alerts = ClassroomAlert.objects.all()

    # Role-based context defaults
    user_dept = None
    if request.user.is_student:
        try:
            student = request.user.student_profile
            user_dept = student.department
            if user_dept and not dept_id:
                alerts = alerts.filter(Q(department=user_dept) | Q(department__isnull=True))
        except Student.DoesNotExist:
            pass
    elif request.user.is_faculty:
        try:
            faculty = request.user.faculty_profile
            user_dept = faculty.department
        except Faculty.DoesNotExist:
            pass

    if dept_id:
        alerts = alerts.filter(department_id=dept_id)

    if alert_type_filter:
        alerts = alerts.filter(alert_type=alert_type_filter)

    if query:
        alerts = alerts.filter(
            Q(title__icontains=query) |
            Q(room_number__icontains=query) |
            Q(subject__icontains=query) |
            Q(message__icontains=query)
        )

    departments = Department.objects.all()

    return render(request, 'departments/classroom_alerts.html', {
        'alerts': alerts,
        'query': query,
        'alert_type_filter': alert_type_filter,
        'dept_id': dept_id,
        'departments': departments,
        'user_dept': user_dept,
    })

@login_required
def classroom_alert_add(request):
    if not (request.user.is_admin or request.user.is_faculty):
        messages.error(request, "Permission denied.")
        return redirect('classroom_alert_list')

    faculty_profile = None
    if request.user.is_faculty:
        try:
            faculty_profile = request.user.faculty_profile
        except Faculty.DoesNotExist:
            pass

    if request.method == 'POST':
        form = ClassroomAlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            if faculty_profile:
                alert.created_by_faculty = faculty_profile
                alert.created_by_name = f"Prof. {faculty_profile.first_name} {faculty_profile.last_name}"
            else:
                alert.created_by_name = "System Admin"
            alert.save()
            messages.success(request, f"Classroom Alert '{alert.title}' created successfully!")
            return redirect('classroom_alert_list')
    else:
        initial_data = {}
        if faculty_profile and faculty_profile.department:
            initial_data['department'] = faculty_profile.department
        if faculty_profile and faculty_profile.subject:
            initial_data['subject'] = faculty_profile.subject
        form = ClassroomAlertForm(initial=initial_data)

    return render(request, 'departments/add_classroom_alert.html', {'form': form, 'is_edit': False})

@login_required
def classroom_alert_edit(request, pk):
    if not (request.user.is_admin or request.user.is_faculty):
        messages.error(request, "Permission denied.")
        return redirect('classroom_alert_list')

    alert = get_object_or_404(ClassroomAlert, pk=pk)

    if request.method == 'POST':
        form = ClassroomAlertForm(request.POST, instance=alert)
        if form.is_valid():
            form.save()
            messages.success(request, f"Classroom Alert '{alert.title}' updated successfully!")
            return redirect('classroom_alert_list')
    else:
        form = ClassroomAlertForm(instance=alert)

    return render(request, 'departments/add_classroom_alert.html', {'form': form, 'alert': alert, 'is_edit': True})

@login_required
def classroom_alert_delete(request, pk):
    if not (request.user.is_admin or request.user.is_faculty):
        messages.error(request, "Permission denied.")
        return redirect('classroom_alert_list')

    alert = get_object_or_404(ClassroomAlert, pk=pk)
    alert.delete()
    messages.success(request, "Classroom Alert deleted successfully.")
    return redirect('classroom_alert_list')

@login_required
def classroom_alert_toggle(request, pk):
    if not (request.user.is_admin or request.user.is_faculty):
        messages.error(request, "Permission denied.")
        return redirect('classroom_alert_list')

    alert = get_object_or_404(ClassroomAlert, pk=pk)
    alert.is_active = not alert.is_active
    alert.save()
    status_text = "activated" if alert.is_active else "deactivated"
    messages.info(request, f"Alert '{alert.title}' has been {status_text}.")
    return redirect('classroom_alert_list')


# --- TIMETABLE VIEWS ---

@login_required
def timetable_view(request):
    dept_id = request.GET.get('dept', '')
    departments = Department.objects.all()

    selected_dept = None
    if dept_id:
        selected_dept = Department.objects.filter(pk=dept_id).first()

    # Default department based on user profile
    if not selected_dept:
        if request.user.is_student:
            try:
                selected_dept = request.user.student_profile.department
            except Student.DoesNotExist:
                pass
        elif request.user.is_faculty:
            try:
                selected_dept = request.user.faculty_profile.department
            except Faculty.DoesNotExist:
                pass

    if not selected_dept and departments.exists():
        selected_dept = departments.first()

    slots = TimetableSlot.objects.filter(is_active=True)
    if selected_dept:
        slots = slots.filter(department=selected_dept)

    days_info = [
        ('Monday', 'MONDAY'),
        ('Tuesday', 'TUESDAY'),
        ('Wednesday', 'WEDNESDAY'),
        ('Thursday', 'THURSDAY'),
        ('Friday', 'FRIDAY'),
        ('Saturday', 'SATURDAY'),
    ]

    days_data = []
    for day_title, day_code in days_info:
        day_slots = [s for s in slots if s.day_of_week == day_code]
        day_slots.sort(key=lambda x: x.start_time)
        days_data.append({
            'title': day_title,
            'code': day_code,
            'slots': day_slots
        })

    return render(request, 'departments/timetable.html', {
        'days_data': days_data,
        'departments': departments,
        'selected_dept': selected_dept,
    })


@login_required
def timetable_add(request):
    if not (request.user.is_admin or request.user.is_faculty):
        messages.error(request, "Permission denied.")
        return redirect('timetable_view')

    faculty_profile = None
    if request.user.is_faculty:
        try:
            faculty_profile = request.user.faculty_profile
        except Faculty.DoesNotExist:
            pass

    if request.method == 'POST':
        form = TimetableSlotForm(request.POST)
        if form.is_valid():
            slot = form.save()
            messages.success(request, f"Timetable slot for '{slot.subject}' created successfully!")
            return redirect('timetable_view')
    else:
        initial_data = {}
        if faculty_profile:
            if faculty_profile.department:
                initial_data['department'] = faculty_profile.department
            initial_data['faculty'] = faculty_profile
            if faculty_profile.subject:
                initial_data['subject'] = faculty_profile.subject
        form = TimetableSlotForm(initial=initial_data)

    return render(request, 'departments/add_timetable.html', {'form': form, 'is_edit': False})

@login_required
def timetable_edit(request, pk):
    if not (request.user.is_admin or request.user.is_faculty):
        messages.error(request, "Permission denied.")
        return redirect('timetable_view')

    slot = get_object_or_404(TimetableSlot, pk=pk)

    if request.method == 'POST':
        form = TimetableSlotForm(request.POST, instance=slot)
        if form.is_valid():
            form.save()
            messages.success(request, f"Timetable slot for '{slot.subject}' updated successfully!")
            return redirect('timetable_view')
    else:
        form = TimetableSlotForm(instance=slot)

    return render(request, 'departments/add_timetable.html', {'form': form, 'slot': slot, 'is_edit': True})

@login_required
def timetable_delete(request, pk):
    if not (request.user.is_admin or request.user.is_faculty):
        messages.error(request, "Permission denied.")
        return redirect('timetable_view')

    slot = get_object_or_404(TimetableSlot, pk=pk)
    slot.delete()
    messages.success(request, "Timetable slot deleted successfully.")
    return redirect('timetable_view')
