from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import date, datetime

from calendar import monthrange
from .models import AppUser, LeaveRequest, Holiday, WorkFromHome, Attendance
from .forms import EmployeeForm, LeaveRequestForm, HolidayForm, WorkFromHomeForm, AttendanceForm
from django.utils import timezone

def redirect_to_login(request):
    return redirect('login')

def logout_view(request):
    request.session.flush()
    return redirect('login')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = AppUser.objects.get(username=username, password=password)
            request.session['user_id'] = user.id
            request.session['role'] = user.role

            if user.role == 'admin':
                return redirect('admin_home')
            elif user.role == 'hr':
                return redirect('hr_home')
            else:
                return redirect('employee_home')
        except AppUser.DoesNotExist:
            return render(request, 'home/login.html', {'error': 'Invalid credentials'})
    return render(request, 'home/login.html')

# --- Dashboard Views ---
def admin_home(request):
    return render(request, 'home/admin_home.html')

def hr_home(request):
    return render(request, 'home/hr_home.html')

def employee_home(request):
    if request.session.get('role') != 'employee':
        return redirect('login')

    user_id = request.session.get('user_id')
    employee = AppUser.objects.get(id=user_id)
    approved_leaves = LeaveRequest.objects.filter(employee=employee, status='approved')

    leave_count = {'annual': 0, 'sick': 0, 'casual': 0}
    for leave in approved_leaves:
        days = (leave.end_date - leave.start_date).days + 1
        leave_count[leave.leave_type] += days

    max_leaves = {'annual': 20, 'sick': 6, 'casual': 6}
    remaining_leaves = {
        key: max(0, max_leaves[key] - leave_count.get(key, 0))
        for key in max_leaves
    }

    return render(request, 'home/employee_home.html', {
        'employee': employee,
        'remaining_leaves': remaining_leaves
    })

# --- HR Actions ---
def add_employee(request):
    if request.session.get('role') != 'hr':
        return redirect('login')

    if request.method == 'POST':
        form = EmployeeForm(request.POST, allowed_roles=['employee'])
        if form.is_valid():
            user = form.save(commit=False)
            if user.role == 'employee':
                user.save()
                return redirect('hr_home')
            else:
                form.add_error('role', 'You are only allowed to add employees.')
    else:
        form = EmployeeForm(allowed_roles=['employee'])

    return render(request, 'home/add_employee.html', {
        'form': form,
        'cancel_url': 'hr_home',
        'base_template': 'home/hr_base.html'  
    })


def employee_list(request):
    if request.session.get('role') != 'hr':
        return redirect('login')

    employees = AppUser.objects.filter(role='employee').select_related('department')
    return render(request, 'home/employee_list.html', {
        'employees': employees,
        'back_url': 'hr_home',
        'base_template': 'home/hr_base.html'  # ✅ ADD THIS LINE
    })


def manage_leaves(request):
    role = request.session.get('role')
    if role not in ['hr', 'admin']:
        return redirect('login')

    leaves = LeaveRequest.objects.select_related('employee')
    base_template = 'home/hr_base.html' if role == 'hr' else 'home/admin_base.html'

    return render(request, 'home/manage_leaves.html', {
        'leaves': leaves,
        'back_url': 'hr_home' if role == 'hr' else 'admin_home',
        'base_template': base_template  # ✅ ADD THIS
    })


def approve_leave(request, leave_id):
    leave = LeaveRequest.objects.get(id=leave_id)
    leave.status = 'approved'
    leave.save()
    messages.success(request, 'Leave approved successfully.')
    return redirect('manage_leaves')

def reject_leave(request, leave_id):
    leave = LeaveRequest.objects.get(id=leave_id)
    leave.status = 'rejected'
    leave.save()
    messages.warning(request, 'Leave rejected.')
    return redirect('manage_leaves')

# --- Leave Handling ---
def apply_leave(request):
    if 'user_id' not in request.session:
        return redirect('login')

    employee = AppUser.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, request.FILES)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = employee
            leave.save()
            return redirect('leave_history')
    else:
        form = LeaveRequestForm()

    return render(request, 'home/apply_leave.html', {'form': form})

def leave_history(request):
    if 'user_id' not in request.session:
        return redirect('login')

    employee = AppUser.objects.get(id=request.session['user_id'])
    leaves = LeaveRequest.objects.filter(employee=employee).order_by('-start_date')
    return render(request, 'home/leave_history.html', {'leaves': leaves})

# --- Work From Home ---
def work_from_home(request):
    if 'user_id' not in request.session:
        return redirect('login')

    employee = AppUser.objects.get(id=request.session['user_id'])

    if request.method == 'POST':
        form = WorkFromHomeForm(request.POST)
        if form.is_valid():
            wfh = form.save(commit=False)
            wfh.employee = employee
            wfh.status = 'pending'
            wfh.save()
            messages.success(request, 'Work From Home request submitted.')
            return redirect('work_from_home_history')
    else:
        form = WorkFromHomeForm()

    return render(request, 'home/work_from_home.html', {'form': form})

def work_from_home_history(request):
    if 'user_id' not in request.session:
        return redirect('login')

    employee = AppUser.objects.get(id=request.session['user_id'])
    wfh_requests = WorkFromHome.objects.filter(employee=employee).order_by('-date')

    return render(request, 'home/work_from_home_history.html', {
        'wfh_requests': wfh_requests
    })

def manage_work_from_home(request):
    if request.session.get('role') not in ['admin', 'hr']:
        return redirect('login')

    wfh_requests = WorkFromHome.objects.select_related('employee').order_by('-date')
    return render(request, 'home/manage_work_from_home.html', {
        'wfh_requests': wfh_requests,
        'back_url': 'hr_home' if request.session.get('role') == 'hr' else 'admin_home'
    })

def approve_wfh(request, wfh_id):
    if request.session.get('role') not in ['admin', 'hr']:
        return redirect('login')

    wfh = WorkFromHome.objects.get(id=wfh_id)
    wfh.status = 'approved'
    wfh.save()
    messages.success(request, "Work From Home approved.")
    return redirect('manage_work_from_home')

def reject_wfh(request, wfh_id):
    if request.session.get('role') not in ['admin', 'hr']:
        return redirect('login')

    wfh = WorkFromHome.objects.get(id=wfh_id)
    wfh.status = 'rejected'
    wfh.save()
    messages.warning(request, "Work From Home rejected.")
    return redirect('manage_work_from_home')

# --- Admin Actions ---
def add_hr(request):
    if request.session.get('role') != 'admin':
        return redirect('login')

    if request.method == 'POST':
        form = EmployeeForm(request.POST, allowed_roles=['hr', 'admin'])
        if form.is_valid():
            user = form.save(commit=False)
            if user.role in ['hr', 'admin']:
                user.save()
                return redirect('admin_home')
            else:
                form.add_error('role', 'You can only add HR or Admins.')
    else:
        form = EmployeeForm(allowed_roles=['hr', 'admin'])

    return render(request, 'home/add_employee.html', {
        'form': form,
        'cancel_url': 'admin_home',
        'base_template': 'home/admin_base.html'  # ✅ So Admin layout is used
    })

def all_employees(request):
    if request.session.get('role') != 'admin':
        return redirect('login')

    employees = AppUser.objects.exclude(role='admin')
    return render(request, 'home/employee_list.html', {
        'employees': employees,
        'back_url': 'admin_home',
        'base_template': 'home/admin_base.html'  # ✅ ADD THIS LINE
    })

def all_leaves(request):
    if request.session.get('role') != 'admin':
        return redirect('login')

    leaves = LeaveRequest.objects.select_related('employee')
    return render(request, 'home/manage_leaves.html', {
        'leaves': leaves,
        'base_template': 'home/admin_base.html',
        'back_url': 'admin_home'
    })

def delete_employee(request):
    if request.session.get('role') != 'admin':
        return redirect('login')

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        try:
            emp = AppUser.objects.get(id=employee_id)
            if emp.role != 'admin':
                emp.delete()
        except AppUser.DoesNotExist:
            pass
        return redirect('delete_employee')

    employees = AppUser.objects.exclude(role='admin')
    return render(request, 'home/delete_employee.html', {'employees': employees})

# --- Holidays ---
def upcoming_holidays(request):
    holidays = Holiday.objects.filter(date__gte=date.today()).order_by('date')
    return render(request, 'home/holidays.html', {'holidays': holidays})

def manage_holidays(request):
    if request.session.get('role') != 'admin':
        return redirect('login')

    holidays = Holiday.objects.all().order_by('date')
    holiday_id = request.GET.get('edit')
    holiday_instance = Holiday.objects.filter(id=holiday_id).first() if holiday_id else None

    if request.method == 'POST':
        form = HolidayForm(request.POST, instance=holiday_instance)
        if form.is_valid():
            form.save()
            if holiday_instance:
                messages.success(request, 'Holiday updated successfully.')
            else:
                messages.success(request, 'Holiday added successfully.')
            return redirect('manage_holidays')
    else:
        form = HolidayForm(instance=holiday_instance)

    return render(request, 'home/manage_holidays.html', {
        'form': form,
        'holidays': holidays,
        'holiday_to_edit': holiday_instance
    })

def delete_holiday(request, holiday_id):
    if request.session.get('role') != 'admin':
        return redirect('login')

    Holiday.objects.filter(id=holiday_id).delete()
    messages.warning(request, "Holiday deleted.")
    return redirect('manage_holidays')

def edit_holiday(request, holiday_id):
    if request.session.get('role') != 'admin':
        return redirect('login')

    holiday = Holiday.objects.get(id=holiday_id)

    if request.method == 'POST':
        form = HolidayForm(request.POST, instance=holiday)
        if form.is_valid():
            form.save()
            messages.success(request, "Holiday updated successfully.")
            return redirect('manage_holidays')
    else:
        form = HolidayForm(instance=holiday)

    return render(request, 'home/edit_holiday.html', {'form': form, 'holiday': holiday})



def attendance_summary(request):
    if request.session.get('role') != 'hr':
        return redirect('login')

    from datetime import date
    today = date.today()
    attendance_records = Attendance.objects.filter(date=today).select_related('employee')

    return render(request, 'home/attendance_summary.html', {
        'attendance_records': attendance_records,
        'date': today,
    })


def approve_wfh(request, wfh_id):
    if request.session.get('role') not in ['admin', 'hr']:
        return redirect('login')

    wfh = WorkFromHome.objects.get(id=wfh_id)
    wfh.status = 'approved'
    wfh.save()

    # Mark attendance
    Attendance.objects.update_or_create(
        employee=wfh.employee,
        date=wfh.date,
        defaults={'work_mode': 'wfh'}
    )

    messages.success(request, "Work From Home approved and attendance marked.")
    return redirect('manage_work_from_home')



def attendance_view(request):
    if request.session.get('role') != 'hr':
        return redirect('login')

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    # Default to today
    if not start_date_str or not end_date_str:
        today = date.today()
        records = Attendance.objects.filter(date=today).select_related('employee')
        start_date_str = end_date_str = today.strftime('%Y-%m-%d')
    else:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            records = Attendance.objects.filter(date__range=(start_date, end_date)).select_related('employee')
        except ValueError:
            records = []

    return render(request, 'home/attendance.html', {
        'records': records,
        'start_date': start_date_str,
        'end_date': end_date_str
    })




def mark_attendance(request):
    if request.session.get('role') != 'employee':
        return redirect('login')

    employee = AppUser.objects.get(id=request.session['user_id'])
    today = datetime.today()

   
    if Attendance.objects.filter(employee=employee, date=today).exists():
        messages.warning(request, "You have already marked attendance for today.")
        return redirect('employee_home')

    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.employee = employee
            attendance.date = today 
            attendance.save()
            messages.success(request, "Attendance submitted successfully.")
            return redirect('employee_home')
    else:
        form = AttendanceForm()

    return render(request, 'home/mark_attendance.html', {'form': form})



def employee_monthly_attendance(request, employee_id):
    if request.session.get('role') != 'hr':
        return redirect('login')

    employee = AppUser.objects.get(id=employee_id)
    today = datetime.today()
    year = today.year
    month = today.month

    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, monthrange(year, month)[1])

    records = Attendance.objects.filter(
        employee=employee,
        date__range=(start_date, end_date)
    ).order_by('date')

    return render(request, 'home/employee_monthly_attendance.html', {
        'employee': employee,
        'records': records,
        'month': today.strftime("%B"),
        'year': year
    })
