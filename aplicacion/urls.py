from django.urls import path
from . import views
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('horarios/', views.horarios, name='horarios'),
    path('datos/', views.datos, name='datos'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registro/', views.registro, name='registro'),
    path('guardar_datos/', views.guardar_datos, name='guardar_datos'),
    path('prediccion/', views.prediccion_view, name='prediccion'),
    path('ver_datos/', views.ver_datos, name='ver_datos'),
    path('modificar_dato/<int:dato_id>/', views.modificar_dato, name='modificar_dato'),
    path('eliminar_dato/<int:dato_id>/', views.eliminar_dato, name='eliminar_dato'),
    path('upload/', views.upload_file_to_s3, name='upload_file_to_s3'),
    path('exportar_excel/', views.exportar_excel, name='exportar_excel'),
]
