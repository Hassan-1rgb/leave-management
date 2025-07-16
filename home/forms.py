from django import forms
from .models import AppUser, LeaveRequest, Holiday, WorkFromHome, Attendance
 

class EmployeeForm(forms.ModelForm):
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        allowed_roles = kwargs.pop('allowed_roles', ['employee', 'hr', 'admin'])
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [(role, role.title()) for role in allowed_roles]

    class Meta:
        model = AppUser
        fields = ['username', 'password', 'email', 'role', 'department', 'employee_code']  # 🔥 added employee_code
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'employee_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. EMP001'
            }),
        }


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason', 'attachment']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.TextInput(attrs={'class': 'form-control'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class HolidayForm(forms.ModelForm):
    class Meta:
        model = Holiday
        fields = ['name', 'date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Holiday Name'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class WorkFromHomeForm(forms.ModelForm):
    class Meta:
        model = WorkFromHome
        fields = ['date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }



class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['work_mode', 'check_in', 'check_out']  # Include check-in/out
        widgets = {
            'work_mode': forms.Select(attrs={'class': 'form-control'}),
            'check_in': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'check_out': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }
