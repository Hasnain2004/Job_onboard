from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Count
from .models import User, Job, Application, ContactSupport
from .forms import SignupForm, LoginForm, JobForm, ApplicationForm, ContactSupportForm

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('job_list')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('job_list')
        
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.full_name}!")
            return redirect('job_list')
    else:
        form = LoginForm()
    
    # Check if user came from social auth
    social_error = request.session.pop('social_auth_error', None)
    if social_error:
        messages.error(request, social_error)
        
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('login')

@login_required
def job_list(request):
    jobs = Job.objects.all().order_by('-created_at')
    search_term = request.GET.get('search', '')
    
    if search_term:
        jobs = jobs.filter(
            title__icontains=search_term
        ) | jobs.filter(
            description__icontains=search_term
        ) | jobs.filter(
            location__icontains=search_term
        )
    
    # Add pagination
    paginator = Paginator(jobs, 10)  # Show 10 jobs per page
    page_number = request.GET.get('page', 1)
    jobs = paginator.get_page(page_number)
    
    return render(request, 'index.html', {
        'jobs': jobs,
        'search_term': search_term
    })

@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'job_detail.html', {'job': job})

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # Check if user already applied for this job
    if Application.objects.filter(job=job, user=request.user).exists():
        messages.error(request, "You have already applied for this job!")
        return redirect('job_list')
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.user = request.user
            application.save()
            messages.success(request, f"Application submitted successfully for {job.title}!")
            return redirect('my_applications')
    else:
        # Pre-fill user information
        initial_data = {
            'applicant_name': request.user.full_name,
            'applicant_email': request.user.email,
        }
        form = ApplicationForm(initial=initial_data)
    
    return render(request, 'apply_job.html', {'form': form, 'job': job})

@login_required
def my_applications(request):
    applications = Application.objects.filter(user=request.user).order_by('-applied_at')
    return render(request, 'my_applications.html', {'applications': applications})

@login_required
def withdraw_application(request, application_id):
    application = get_object_or_404(Application, id=application_id, user=request.user)
    if request.method == 'POST':
        application.delete()
        messages.success(request, "Application withdrawn successfully")
    return redirect('my_applications')

@login_required
def application_details_api(request, application_id):
    application = get_object_or_404(Application, id=application_id, user=request.user)
    data = {
        'id': application.id,
        'job_title': application.job.title,
        'applicant_name': application.applicant_name,
        'applicant_email': application.applicant_email,
        'applied_at': application.applied_at.isoformat(),
        'status': application.status,
    }
    return JsonResponse(data)

@login_required
def contact_support(request):
    if request.method == 'POST':
        form = ContactSupportForm(request.POST)
        if form.is_valid():
            support_ticket = form.save(commit=False)
            support_ticket.user = request.user
            support_ticket.save()
            messages.success(request, "Your message has been sent successfully! We'll get back to you soon.")
            return redirect('job_list')
    else:
        # Pre-fill user information
        initial_data = {
            'name': request.user.full_name,
            'email': request.user.email,
        }
        form = ContactSupportForm(initial=initial_data)
    
    return render(request, 'contact.html', {'form': form})

# Admin Dashboard Views
@login_required
def admin_dashboard(request):
    # Check if user is admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('job_list')
    
    # Get statistics
    jobs_count = Job.objects.count()
    applications_count = Application.objects.count()
    users_count = User.objects.filter(is_active=True).count()
    support_tickets_count = ContactSupport.objects.count()
    
    # Recent jobs and applications
    recent_jobs = Job.objects.order_by('-created_at')[:5]
    recent_applications = Application.objects.order_by('-applied_at')[:5]
    
    context = {
        'jobs_count': jobs_count,
        'applications_count': applications_count,
        'users_count': users_count,
        'support_tickets_count': support_tickets_count,
        'recent_jobs': recent_jobs,
        'recent_applications': recent_applications
    }
    
    return render(request, 'admin_dashboard.html', context)

@login_required
def manage_jobs(request):
    # Check if user is admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to manage jobs.")
        return redirect('job_list')
    
    jobs = Job.objects.all()
    search_term = request.GET.get('search', '')
    sort_option = request.GET.get('sort', 'newest')
    
    # Apply search filter
    if search_term:
        jobs = jobs.filter(
            title__icontains=search_term
        ) | jobs.filter(
            description__icontains=search_term
        ) | jobs.filter(
            location__icontains=search_term
        )
    
    # Apply sorting
    if sort_option == 'oldest':
        jobs = jobs.order_by('created_at')
    elif sort_option == 'title_asc':
        jobs = jobs.order_by('title')
    elif sort_option == 'title_desc':
        jobs = jobs.order_by('-title')
    elif sort_option == 'applications':
        jobs = jobs.annotate(app_count=Count('applications')).order_by('-app_count')
    else:  # Default is newest
        jobs = jobs.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(jobs, 10)  # Show 10 jobs per page
    page_number = request.GET.get('page', 1)
    jobs = paginator.get_page(page_number)
    
    return render(request, 'manage_jobs.html', {
        'jobs': jobs,
        'search_term': search_term,
        'sort_option': sort_option
    })

@login_required
def create_job(request):
    # Check if user is admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to create jobs.")
        return redirect('job_list')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.created_by = request.user
            job.save()
            messages.success(request, "Job created successfully!")
            return redirect('manage_jobs')
    else:
        form = JobForm()
    
    return render(request, 'create_job.html', {'form': form})

@login_required
def edit_job(request, job_id):
    # Check if user is admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to edit jobs.")
        return redirect('job_list')
    
    job = get_object_or_404(Job, id=job_id)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect('manage_jobs')
    else:
        form = JobForm(instance=job)
    
    return render(request, 'create_job.html', {'form': form, 'job': job})

@login_required
def delete_job(request, job_id):
    # Check if user is admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to delete jobs.")
        return redirect('job_list')
    
    job = get_object_or_404(Job, id=job_id)
    
    if request.method == 'POST':
        job.delete()
        messages.success(request, "Job deleted successfully!")
    
    return redirect('manage_jobs')

@login_required
def job_applications(request, job_id):
    # Check if user is admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to view applications.")
        return redirect('job_list')
    
    job = get_object_or_404(Job, id=job_id)
    applications = job.applications.all()
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    # Sort applications
    sort_option = request.GET.get('sort', 'newest')
    if sort_option == 'oldest':
        applications = applications.order_by('applied_at')
    elif sort_option == 'name_asc':
        applications = applications.order_by('applicant_name')
    elif sort_option == 'name_desc':
        applications = applications.order_by('-applicant_name')
    else:  # Default is newest
        applications = applications.order_by('-applied_at')
    
    # Pagination
    paginator = Paginator(applications, 12)  # Show 12 applications per page
    page_number = request.GET.get('page', 1)
    applications = paginator.get_page(page_number)
    
    return render(request, 'job_applications.html', {
        'job': job,
        'applications': applications,
        'status_filter': status_filter,
        'sort_option': sort_option
    })

@login_required
def application_detail(request, application_id):
    # Check if user is admin or the application owner
    application = get_object_or_404(Application, id=application_id)
    
    if request.user.role != 'admin' and application.user != request.user:
        messages.error(request, "You don't have permission to view this application.")
        return redirect('job_list')
    
    return render(request, 'application_detail.html', {'application': application})

@login_required
@require_POST
def update_application_status(request, application_id):
    # Check if user is admin
    if request.user.role != 'admin':
        return HttpResponseForbidden("You don't have permission to update application status.")
    
    application = get_object_or_404(Application, id=application_id)
    new_status = request.POST.get('status')
    notes = request.POST.get('notes', '')
    
    if new_status in dict(Application.STATUS_CHOICES).keys():
        application.status = new_status
        if notes:
            application.notes = notes
        application.save()
        messages.success(request, f"Application status updated to {application.get_status_display()}")
    
    return redirect('job_applications', job_id=application.job.id)

@login_required
def manage_applications(request):
    # Check if user is admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to manage applications.")
        return redirect('job_list')
    
    applications = Application.objects.all()
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    # Sort applications
    sort_option = request.GET.get('sort', 'newest')
    if sort_option == 'oldest':
        applications = applications.order_by('applied_at')
    elif sort_option == 'job_asc':
        applications = applications.order_by('job__title')
    elif sort_option == 'job_desc':
        applications = applications.order_by('-job__title')
    elif sort_option == 'name_asc':
        applications = applications.order_by('applicant_name')
    elif sort_option == 'name_desc':
        applications = applications.order_by('-applicant_name')
    else:  # Default is newest
        applications = applications.order_by('-applied_at')
    
    # Pagination
    paginator = Paginator(applications, 15)  # Show 15 applications per page
    page_number = request.GET.get('page', 1)
    applications = paginator.get_page(page_number)
    
    return render(request, 'manage_applications.html', {
        'applications': applications,
        'status_filter': status_filter,
        'sort_option': sort_option
    })

@login_required
def support_tickets(request):
    # Check if user is admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to view support tickets.")
        return redirect('job_list')
    
    tickets = ContactSupport.objects.all().order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(tickets, 15)  # Show 15 tickets per page
    page_number = request.GET.get('page', 1)
    tickets = paginator.get_page(page_number)
    
    return render(request, 'support_tickets.html', {
        'tickets': tickets,
        'status_filter': status_filter
    })

def handle_auth_callback(request):
    """
    Handle OAuth callbacks and errors
    """
    # Check for error in the request
    if 'error' in request.GET:
        error = request.GET.get('error')
        error_description = request.GET.get('error_description', 'Authentication failed')
        
        # Store error in session to display it on login page
        request.session['social_auth_error'] = f"Google login failed: {error_description}"
        return redirect('login')
    
    # Successful authentication should be handled by social_django
    # This is just a fallback redirect
    if request.user.is_authenticated:
        messages.success(request, f"Welcome, {request.user.full_name}! You've successfully signed in with Google.")
        return redirect('job_list')
    else:
        return redirect('login')
