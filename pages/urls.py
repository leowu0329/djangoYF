from django.urls import path
from . import views
from .views import (
    CaseListView,
    CaseDetailView,
    CaseCreateView,
    CaseUpdateView,
    CaseDeleteView
)

urlpatterns = [
	path('', views.home_page, name='home'),
    path('cases/', CaseListView.as_view(), name='case_list'),
    path('cases/<int:pk>/', CaseDetailView.as_view(), name='case_detail'),
    path('cases/new/', CaseCreateView.as_view(), name='case_create'),
    path('cases/<int:pk>/update/', CaseUpdateView.as_view(), name='case_update'),
    path('cases/<int:pk>/delete/', CaseDeleteView.as_view(), name='case_delete'),

    # Land
    path('cases/<int:case_pk>/lands/new/', views.LandCreateView.as_view(), name='land_create'),
    path('lands/<int:pk>/update/', views.LandUpdateView.as_view(), name='land_update'),
    path('lands/<int:pk>/delete/', views.LandDeleteView.as_view(), name='land_delete'),

    # Build
    path('cases/<int:case_pk>/builds/new/', views.BuildCreateView.as_view(), name='build_create'),
    path('builds/<int:pk>/update/', views.BuildUpdateView.as_view(), name='build_update'),
    path('builds/<int:pk>/delete/', views.BuildDeleteView.as_view(), name='build_delete'),

    # Person
    path('cases/<int:case_pk>/people/new/', views.PersonCreateView.as_view(), name='person_create'),
    path('people/<int:pk>/update/', views.PersonUpdateView.as_view(), name='person_update'),
    path('people/<int:pk>/delete/', views.PersonDeleteView.as_view(), name='person_delete'),

    # Survey
    path('cases/<int:case_pk>/surveys/new/', views.SurveyCreateView.as_view(), name='survey_create'),
    path('surveys/<int:pk>/update/', views.SurveyUpdateView.as_view(), name='survey_update'),
    path('surveys/<int:pk>/delete/', views.SurveyDeleteView.as_view(), name='survey_delete'),

    # FinalDecision
    path('cases/<int:case_pk>/finaldecisions/new/', views.FinalDecisionCreateView.as_view(), name='finaldecision_create'),
    path('finaldecisions/<int:pk>/update/', views.FinalDecisionUpdateView.as_view(), name='finaldecision_update'),
    path('finaldecisions/<int:pk>/delete/', views.FinalDecisionDeleteView.as_view(), name='finaldecision_delete'),

    # Result
    path('cases/<int:case_pk>/results/new/', views.ResultCreateView.as_view(), name='result_create'),
    path('results/<int:pk>/update/', views.ResultUpdateView.as_view(), name='result_update'),
    path('results/<int:pk>/delete/', views.ResultDeleteView.as_view(), name='result_delete'),

    # ObjectBuild
    path('cases/<int:case_pk>/objectbuilds/new/', views.ObjectBuildCreateView.as_view(), name='objectbuild_create'),
    path('objectbuilds/<int:pk>/update/', views.ObjectBuildUpdateView.as_view(), name='objectbuild_update'),
    path('objectbuilds/<int:pk>/delete/', views.ObjectBuildDeleteView.as_view(), name='objectbuild_delete'),
]