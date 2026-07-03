from django.urls import path

from .views import LoginView, RegistroView, YoView

urlpatterns = [
    path("registro", RegistroView.as_view(), name="auth-registro"),
    path("login", LoginView.as_view(), name="auth-login"),
    path("yo", YoView.as_view(), name="auth-yo"),
]
