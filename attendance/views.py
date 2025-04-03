from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import OTP, AttendanceRecord
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404

# Decorator to ensure only admin users can access OTP generation page
def admin_check(user):
    return user.is_staff  # Only allow users with is_staff set to True



def register(request):
    context = {
        'username': '',
        'email': '',
        'password': '',
        'password_confirm': '',
    }

    if request.method == 'POST':
        context['username'] = request.POST.get('username')
        context['email'] = request.POST.get('email')
        context['password'] = request.POST.get('password')
        context['password_confirm'] = request.POST.get('password_confirm')

        if context['password'] == context['password_confirm']:
            if User.objects.filter(username=context['username']).exists():
                messages.error(request, 'Username already exists')
            elif User.objects.filter(email=context['email']).exists():
                messages.error(request, 'Email already registered')
            else:
                User.objects.create_user(username=context['username'], email=context['email'], password=context['password'])
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')

    return render(request, 'attendance/register.html', context)




# User Login View
def user_login(request):
    """User login view."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to dashboard after login
        else:
            messages.error(request, "Invalid credentials. Please try again.")
    return render(request, 'attendance/login.html')

def logout_user(request):
    logout(request)
    return redirect('login')

# Admin OTP Generation View
@user_passes_test(admin_check)
def admin_otp(request):
    """Generate OTP only accessible by admin users."""
    otp_code = OTP.generate_otp()  # Generate a random OTP
    otp_instance = OTP.objects.create(otp_code=otp_code)  # Save OTP to the database

    # Display generated OTP on the admin page
    context = {
        'otp_code': otp_code,
        'created_at': otp_instance.created_at,
        
    }

    return render(request, 'attendance/admin_otp.html', context)



# User Dashboard View
@login_required
def dashboard(request):
    """Dashboard showing user attendance options."""
    return render(request, 'attendance/dashboard.html')


# Handle Employee Entry/Exit Action
@login_required
def employee_action(request, action):
    """Handle employee entry/exit actions."""
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        # Fetch the most recent valid OTP (within last 3 minutes)
        otp_qs = OTP.objects.filter(created_at__gte=timezone.now()-timezone.timedelta(minutes=3)).order_by('-created_at')
        if not otp_qs.exists():
            messages.error(request, "No valid OTP available. Please ask the admin for a new OTP.")
            return redirect('employee-action', action=action)

        otp_instance = otp_qs.first()
        if user_otp == otp_instance.otp_code and otp_instance.is_valid():
            # Log the attendance record
            attendance, created = AttendanceRecord.objects.get_or_create(
                user=request.user, date=timezone.now().date()
            )
            if action == "enter":
                attendance.entry_time = timezone.now()
            elif action == "exit":
                attendance.exit_time = timezone.now()
            attendance.save()
            otp_instance.delete()

            messages.success(request, f"Your {action} time has been logged.")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid or expired OTP. Please try again.")
            return redirect('employee-action', action=action)

    return render(request, 'attendance/enter_exit.html', {'action': action})



# Decorator to ensure only admin users can access the user list page
def admin_check(user):
    return user.is_staff  # Only allow users with is_staff set to True

@user_passes_test(admin_check)
def user_list(request):
    """Display a list of all users."""
    users = User.objects.all()  # Fetch all users
    context = {
        'users': users
    }
    return render(request, 'attendance/user_list.html', context)


@user_passes_test(admin_check)
def user_attendance(request, user_id):
    """Display a list of entry and exit times for a specific user."""
    user = get_object_or_404(User, id=user_id)  # Get the user by ID
    attendance_records = AttendanceRecord.objects.filter(user=user).order_by('-date')  # Get attendance records for the user
    context = {
        'user': user,
        'attendance_records': attendance_records
    }
    return render(request, 'attendance/user_attendance.html', context)
