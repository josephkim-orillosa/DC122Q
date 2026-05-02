from functools import wraps

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AccountEditForm, EventForm, LoginForm, RegisterForm, StudentForm
from .models import AccountProfile, Event


def get_account_profile(user):
    profile, _ = AccountProfile.objects.get_or_create(
        user=user,
        defaults={"account_type": AccountProfile.STUDENT},
    )
    return profile


def role_required(required_account_type):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            profile = get_account_profile(request.user)
            if profile.account_type != required_account_type:
                return redirect('dashboard_redirect')
            return view_func(request, *args, **kwargs)

        return wrapped_view

    return decorator


def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    return redirect('login')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('dashboard_redirect')

    return render(request, 'login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('dashboard_redirect')

    return render(request, 'register.html', {'form': form})


@login_required
def dashboard_redirect(request):
    profile = get_account_profile(request.user)
    if profile.account_type == AccountProfile.TEACHER:
        return redirect('teacher_dashboard')
    return redirect('student_dashboard')


@login_required
@role_required(AccountProfile.STUDENT)
def student_dashboard(request):
    events = Event.objects.select_related('teacher').prefetch_related('participants')
    joined_event_ids = list(request.user.joined_events.values_list('id', flat=True))
    return render(
        request,
        'student_dashboard.html',
        {'events': events, 'joined_event_ids': joined_event_ids},
    )


@login_required
@role_required(AccountProfile.TEACHER)
def teacher_dashboard(request):
    return render(request, 'teacher_dashboard.html')


@login_required
@role_required(AccountProfile.TEACHER)
def event_planner(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.teacher = request.user
            event.save()
            messages.success(request, 'Event created successfully.')
            return redirect('event_planner')
    else:
        form = EventForm()

    events = request.user.managed_events.prefetch_related('participants')
    return render(request, 'event_planner.html', {'form': form, 'events': events})


@login_required
@role_required(AccountProfile.TEACHER)
@require_POST
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, teacher=request.user)
    event.delete()
    messages.success(request, 'Event deleted successfully.')
    return redirect('event_planner')


@login_required
@role_required(AccountProfile.STUDENT)
@require_POST
def join_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.participants.add(request.user)
    messages.success(request, 'You joined the event.')
    return redirect('student_dashboard')


@login_required
@role_required(AccountProfile.STUDENT)
@require_POST
def leave_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.participants.remove(request.user)
    messages.success(request, 'You left the event.')
    return redirect('student_dashboard')


@login_required
def edit_account(request):
    form = AccountEditForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Account updated successfully.')
        return redirect('dashboard_redirect')

    return render(request, 'edit_account.html', {'form': form})


@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return redirect('dashboard_redirect')


@login_required
@role_required(AccountProfile.TEACHER)
def addNewStudent(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student record saved successfully.')
            return redirect('teacher_dashboard')
    else:
        form = StudentForm()

    return render(request, 'addNewStudent.html', {'form': form})
