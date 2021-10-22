from django.urls import path
from . import views

urlpatterns = [
    path("",views.index,name="index"),
    path("register/",views.register,name="register"),
    path('registerFace/', views.registerFace, name='registerFace'),
    path('login/',views.login,name='login'),
    path('loginFace/',views.loginFace,name='loginFace'),
]