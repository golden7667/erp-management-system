from django import forms
from .models import ClassroomAlert, TimetableSlot, Department
from faculty.models import Faculty

class ClassroomAlertForm(forms.ModelForm):
    class Meta:
        model = ClassroomAlert
        fields = ['title', 'alert_type', 'priority', 'room_number', 'subject', 'department', 'message', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Lab Relocation or Class Cancellation'}),
            'alert_type': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Room 302 / LH-01'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Data Structures'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Provide detailed explanation or instructions for students...'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class TimetableSlotForm(forms.ModelForm):
    class Meta:
        model = TimetableSlot
        fields = ['department', 'subject', 'faculty', 'day_of_week', 'start_time', 'end_time', 'room_number', 'semester_or_year', 'is_active']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Operating Systems'}),
            'faculty': forms.Select(attrs={'class': 'form-select'}),
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Room 102 / Lab 3'}),
            'semester_or_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Semester 3 / 2nd Year'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
