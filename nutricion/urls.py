# nutricion/urls.py

from django.urls import path
from . import views, views_auth
from .views_cbv import RegistroListView, RegistroCreateView, HabitoCreateView, PerfilUpdateView

app_name = "nutricion"

urlpatterns = [
    # ======================
    # DASHBOARD
    # ======================
    path("", views.dashboard, name="dashboard"),

    # ======================
    # AUTH
    # ======================
    path("login/", views_auth.login_view, name="login"),
    path("logout/", views_auth.logout_view, name="logout"),
    path("registro/", views_auth.registro_view, name="registro"),

    # ======================
    # PERFIL (FBV + CBV)
    # ======================
    path("perfil/", views_auth.perfil_view, name="perfil"),
    path("perfil/editar/", PerfilUpdateView.as_view(), name="perfil_editar"),

    # ======================
    # COMIDAS (FBV)
    # ======================
    path("comidas/", views.lista_comidas, name="lista_comidas"),
    path("comidas/nueva/", views.crear_comida, name="crear_comida"),

    # ======================
    # COMIDAS (CBV)
    # ======================
    path("comidas/cbv/", RegistroListView.as_view(), name="lista_comidas_cbv"),
    path("comidas/cbv/nueva/", RegistroCreateView.as_view(), name="crear_comida_cbv"),

    # ======================
    # HÁBITOS
    # ======================
    path("habitos/", views.lista_habitos, name="lista_habitos"),
    path("habitos/nuevo/", HabitoCreateView.as_view(), name="crear_habito"),

    # ======================
    # LOGROS
    # ======================
    path("logros/", views.logros_view, name="logros"),
]