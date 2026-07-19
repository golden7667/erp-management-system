from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Count, Avg

from .models import User
from .forms import UserRegisterForm
from students.models import Student
from faculty.models import Faculty
from departments.models import Department

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_home')
        
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Send verification email mock/simulated
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_link = request.build_absolute_uri(
                f"/accounts/verify/{uid}/{token}/"
            )
            
            # Simple mock send mail log to console / stdout
            print(f"--- EMAIL VERIFICATION LINK FOR {user.username} ---")
            print(verification_link)
            print("-------------------------------------------------")
            
            messages.success(request, "Account created successfully! Please verify your email using the link sent to your console/logs.")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Welcome back, {username}!")
                return redirect('dashboard_home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('login')

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        users = User.objects.filter(email=email)
        if users.exists():
            for user in users:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_link = request.build_absolute_uri(
                    f"/accounts/reset/{uid}/{token}/"
                )
                print(f"--- PASSWORD RESET LINK FOR {user.username} ---")
                print(reset_link)
                print("----------------------------------------------")
            messages.success(request, "Password reset instructions have been generated in system logs/console.")
        else:
            messages.error(request, "No user with this email address exists.")
    return render(request, 'registration/forgot_password.html')

def verify_email_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.email_verified = True
        user.save()
        messages.success(request, "Your email has been verified! You can now login.")
        return redirect('login')
    else:
        messages.error(request, "The verification link was invalid or has expired.")
        return redirect('login')

@login_required
def dashboard_home(request):
    if request.user.is_admin:
        return redirect('admin_dashboard')
    elif request.user.is_faculty:
        return redirect('faculty_dashboard')
    elif request.user.is_student:
        return redirect('student_dashboard')
    return render(request, 'dashboard/visitor.html')

@login_required
def admin_dashboard(request):
    if not request.user.is_admin:
        return redirect('dashboard_home')
        
    total_students = Student.objects.count()
    total_faculty = Faculty.objects.count()
    total_departments = Department.objects.count()
    
    # Simple analytics grouping (done in Python to support cross-database SQLite setup)
    students_by_dept_id = Student.objects.values('department_id').annotate(count=Count('id'))
    dept_mapping = {d.id: d.name for d in Department.objects.all()}
    
    chart_category_labels = []
    chart_category_values = []
    for item in students_by_dept_id:
        dept_id = item['department_id']
        dept_name = dept_mapping.get(dept_id, 'Unassigned') if dept_id is not None else 'Unassigned'
        chart_category_labels.append(dept_name)
        chart_category_values.append(item['count'])
    
    # If no data, use mock data fallback for layout preview
    if not chart_category_labels:
        chart_category_labels = ['Computer Science', 'Mechanical Eng', 'Electrical Eng', 'Civil Eng']
        chart_category_values = [15, 8, 12, 5]
        
    # Calculate average GPA grouped by department
    gpa_by_dept = Student.objects.values('department_id').annotate(avg_gpa=Avg('semester_result_gpa'))
    chart_sales_labels = []
    chart_sales_values = []
    for item in gpa_by_dept:
        dept_id = item['department_id']
        dept_name = dept_mapping.get(dept_id, 'Unassigned') if dept_id is not None else 'Unassigned'
        chart_sales_labels.append(dept_name)
        chart_sales_values.append(round(item['avg_gpa'] or 0.0, 2))
        
    if not chart_sales_labels:
        chart_sales_labels = ['CSE', 'EE', 'ME']
        chart_sales_values = [8.5, 7.8, 8.2]
        
    context = {
        'total_students': total_students,
        'total_faculty': total_faculty,
        'total_departments': total_departments,
        'chart_sales_labels': chart_sales_labels,
        'chart_sales_values': chart_sales_values,
        'chart_category_labels': chart_category_labels,
        'chart_category_values': chart_category_values,
        'recent_students': Student.objects.prefetch_related('department').order_by('-id')[:5],
        'recent_faculty': Faculty.objects.prefetch_related('department').order_by('-id')[:5]
    }
    return render(request, 'dashboard/admin.html', context)

@login_required
def faculty_dashboard(request):
    if not request.user.is_faculty:
        return redirect('dashboard_home')
        
    try:
        faculty_profile = request.user.faculty_profile
    except Faculty.DoesNotExist:
        faculty_profile = None
        
    context = {
        'faculty_profile': faculty_profile,
        'total_students': Student.objects.filter(department=faculty_profile.department).count() if faculty_profile else 0,
        'my_students': Student.objects.filter(department=faculty_profile.department) if faculty_profile else [],
        'user': request.user,
    }
    return render(request, 'dashboard/faculty.html', context)

@login_required
def student_dashboard(request):
    if not request.user.is_student:
        return redirect('dashboard_home')
        
    try:
        student_profile = request.user.student_profile
    except Student.DoesNotExist:
        student_profile = None
        
    context = {
        'student_profile': student_profile,
        'user': request.user,
    }
    return render(request, 'dashboard/student.html', context)

def password_reset_confirm_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if password1 == password2:
                user.set_password(password1)
                user.save()
                messages.success(request, "Your password has been successfully reset! You can now login.")
                return redirect('login')
            else:
                messages.error(request, "Passwords do not match.")
        return render(request, 'registration/password_reset_confirm.html')
    else:
        messages.error(request, "The password reset link was invalid or has expired.")

# Role‑specific login helpers
def _role_login(request, role):
    """Common login logic for a specific user role.

    - ``role``: one of ``'STUDENT'``, ``'FACULTY'``, ``'ADMIN'``
    """
    if request.user.is_authenticated:
        return redirect('dashboard_home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and getattr(user, f'is_{role.lower()}', False):
                login(request, user)
                messages.info(request, f"Welcome back, {username}!")
                return redirect('dashboard_home')
            else:
                messages.error(request, "Invalid credentials or role mismatch.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form, 'active_role': role.lower()})

def student_login_view(request):
    if request.method == 'GET':
        next_url = request.GET.get('next', '')
        redirect_url = '/accounts/login/?role=student'
        if next_url:
            redirect_url += f'&next={next_url}'
        return redirect(redirect_url)
    return _role_login(request, role='STUDENT')

def faculty_login_view(request):
    if request.method == 'GET':
        next_url = request.GET.get('next', '')
        redirect_url = '/accounts/login/?role=faculty'
        if next_url:
            redirect_url += f'&next={next_url}'
        return redirect(redirect_url)
    return _role_login(request, role='FACULTY')

def admin_login_view(request):
    if request.method == 'GET':
        next_url = request.GET.get('next', '')
        redirect_url = '/accounts/login/?role=admin'
        if next_url:
            redirect_url += f'&next={next_url}'
        return redirect(redirect_url)
    return _role_login(request, role='ADMIN')

# Admin can reset password for any user (student or faculty)
def admin_change_user_password(request, user_id):
    if not request.user.is_admin:
        messages.error(request, "Permission denied.")
        return redirect('dashboard_home')
    target_user = User.objects.filter(pk=user_id).first()
    if not target_user:
        messages.error(request, "User not found.")
        return redirect('admin_dashboard')
    if request.method == 'POST':
        pwd1 = request.POST.get('new_password1')
        pwd2 = request.POST.get('new_password2')
        if pwd1 and pwd1 == pwd2:
            target_user.set_password(pwd1)
            target_user.save()
            messages.success(request, f"Password for {target_user.username} updated.")
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Passwords do not match.")
    return render(request, 'registration/admin_change_password.html', {'user': target_user})

