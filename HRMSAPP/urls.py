from django.urls import path
from .views import *

urlpatterns = [
    path("signup/", HRSignupView.as_view(), name="hr-signup"),
    path("login/", HRLoginView.as_view(), name="hr-login"),
    path("logout/", HRLogoutView.as_view(), name="hr-logout"),
    path('candidates/', CandidateView.as_view(), name='add-candidate'),
    path('candidates/<int:pk>/', CandidateGetUpdateDeleteView.as_view(), name='add-candidate-id'),
    path('domain-interests/', DomainInterestView.as_view(), name='domain-interest'),
    path('domain-interests/<int:pk>/', DomainInterestUpdateDeleteView.as_view(), name='domain-interest-id'),
    path('tech-areas/', TechAreaCreateGetView.as_view(), name='tech-area'),
    path('tech-areas/<int:pk>/', TechAreaUpdateDeleteView.as_view(), name='tech-area-id'),
    path('qualifications/', QualificationCreateView.as_view(), name='qualification'),
    path('qualifications/<int:pk>/', QualificationUpdateDeleteView.as_view(), name='qualification-id'),
    path('candidate-tech-areas/', CandidateTechAreaView.as_view(), name='candidate-tech-area'),
    path('candidate-tech-areas/<int:pk>/', CandidateTechAreaUpdateDeleteView.as_view(), name='candidate-tech-area-id'),
    path('schedule-interviews/', ScheduleInterviewCreate.as_view(), name='schedule_interview'),
    path('schedule-interviews/<int:pk>/', InterviewUpdateDelete.as_view(), name='schedule-interview-is'),
    path('candidates/search/', Search.as_view(), name='search-api'),
    path('candidates/search/qualification', QualificationSearch.as_view(), name='search-api-qualification'),

    ]
