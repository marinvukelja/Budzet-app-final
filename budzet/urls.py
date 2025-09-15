from django.contrib import admin
from django.urls import path
from core.views import (
    register,
    MyLoginView,
    dashboard,
    kategorije_list_create,
    transakcije_list_create,
    ciljevi_list_create,
    transakcije_export_csv,
    logout_view,
    racuni_list_create,
    budzeti_list_create,
    ponavljajuce_transakcije_list_create,
    process_recurring_transactions,
    budget_analysis,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("register/", register, name="register"),
    path("login/", MyLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"), 
    path("", dashboard, name="dashboard"),
    path("kategorije/", kategorije_list_create, name="kategorije"),
    path("transakcije/", transakcije_list_create, name="transakcije"),
    path("transakcije/export/", transakcije_export_csv, name="transakcije_export"),
    path("racuni/", racuni_list_create, name="racuni"),
    path("budzeti/", budzeti_list_create, name="budzeti"),
    path("ponavljajuce/", ponavljajuce_transakcije_list_create, name="ponavljajuce"),
    path("ponavljajuce/process/", process_recurring_transactions, name="process_recurring"),
    path("ciljevi/", ciljevi_list_create, name="ciljevi"),
    path("analiza/", budget_analysis, name="budget_analysis"),
]
