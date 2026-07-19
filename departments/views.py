from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Department

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
