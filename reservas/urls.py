from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import views_api

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

    path('api/voos/', views_api.lista_voos),
    path('api/voos/<int:id>/', views_api.detalhe_voo),
    path('api/reservas/', views_api.criar_reserva),

    # NOVAS ROTAS DE AUTH PARA O ANGULAR
    path('api/signup/', views_api.api_signup),
    path('api/login/', views_api.api_login),
]