from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "reservas"

urlpatterns = [
    path("", views.home, name="home"),
    path("voos/", views.voos_list, name="voos_list"),
    path("voos/<int:voo_id>/", views.voo_detail, name="voo_detail"),
    path("reservar/<int:assento_id>/", views.reservar_assento, name="reservar_assento"),
    path("minhas-reservas/", views.minhas_reservas, name="minhas_reservas"),

    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="reservas/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]