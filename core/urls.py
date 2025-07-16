"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path('', views.redirect_to_login),  # Optional: root redirect
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-home/', views.admin_home, name='admin_home'),
    path('hr-home/', views.hr_home, name='hr_home'),
    path('employee-home/', views.employee_home, name='employee_home'),

    # Employee features
    path('apply-leave/', views.apply_leave, name='apply_leave'),
    path('leave-history/', views.leave_history, name='leave_history'),

    # HR features
    path('add-employee/', views.add_employee, name='add_employee'),
    path('employee-list/', views.employee_list, name='employee_list'),

    path('manage-leaves/', views.manage_leaves, name='manage_leaves'),
    path('approve-leave/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('reject-leave/<int:leave_id>/', views.reject_leave, name='reject_leave'),

    path('add-hr/', views.add_hr, name='add_hr'),
    path('all-employees/', views.all_employees, name='all_employees'),
    path('all-leaves/', views.all_leaves, name='all_leaves'),
    path('delete-employee/', views.delete_employee, name='delete_employee'),

   path('holidays/', views.upcoming_holidays, name='upcoming_holidays'),
   path('manage-holidays/', views.manage_holidays, name='manage_holidays'),
   path('delete-holiday/<int:holiday_id>/', views.delete_holiday, name='delete_holiday'),
   
   path('edit-holiday/<int:holiday_id>/', views.edit_holiday, name='edit_holiday'),

   path('work-from-home/', views.work_from_home, name='work_from_home'),
   path('work-from-home-history/', views.work_from_home_history, name='work_from_home_history'),
   path('manage-work-from-home/', views.manage_work_from_home, name='manage_work_from_home'),
   path('approve-wfh/<int:wfh_id>/', views.approve_wfh, name='approve_wfh'),
   path('reject-wfh/<int:wfh_id>/', views.reject_wfh, name='reject_wfh'),
   path('attendance/', views.attendance_view, name='attendance'),
   path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
   path('attendance/<int:employee_id>/month/', views.employee_monthly_attendance, name='employee_monthly_attendance'),


]

