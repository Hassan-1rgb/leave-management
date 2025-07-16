from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'department'

    def __str__(self):
        return self.name


class AppUser(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('hr', 'HR'),
        ('employee', 'Employee'),
    ]

    username = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    employee_code = models.CharField(max_length=10, unique=True, null=True, blank=True)

    class Meta:
        db_table = 'appusers'

    def __str__(self):
        return self.username


class LeaveRequest(models.Model):
    LEAVE_CHOICE = [
        ('casual', 'Casual'),
        ('annual', 'Annual'),
        ('sick', 'Sick'),
    ]

    STATUS_CHOICE = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    employee = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_CHOICE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, default='pending')

    class Meta:
        db_table = 'leaverequest'

    def __str__(self):
        return f"{self.employee.username} - {self.leave_type} ({self.status})"


class Holiday(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField(unique=True)

    class Meta:
        db_table = 'holiday'

    def __str__(self):
        return f"{self.name} ({self.date})"


class WorkFromHome(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    employee = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    class Meta:
        db_table = 'work_from_home'

    def __str__(self):
        return f"{self.employee.username} - {self.date}"


class Attendance(models.Model):
    WORK_MODES = [
        ('office', 'Office'),
        ('wfh', 'Work From Home'),
    ]

    employee = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    work_mode = models.CharField(max_length=10, choices=WORK_MODES)

    class Meta:
        unique_together = ('employee', 'date')
        db_table = 'attendance'

    def __str__(self):
        return f"{self.employee.username} - {self.date} - {self.get_work_mode_display()}"
