from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('account/edit/', views.edit_account, name='edit_account'),
    path('logout/', views.logout_view, name='logout'),
    path('addNewStudent/', views.addNewStudent, name='addNewStudent'),
    path('events/', views.event_planner, name='event_planner'),
    path('events/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('events/<int:event_id>/join/', views.join_event, name='join_event'),
    path('events/<int:event_id>/leave/', views.leave_event, name='leave_event'),
]
