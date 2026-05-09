# nutricion/views_cbv.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from .models import RegistroComida, RegistroHabito, PerfilUsuario
from .forms import RegistroHabitoForm, PerfilForm


# =========================
# LISTA DE REGISTROS (CBV)
# =========================
class RegistroListView(LoginRequiredMixin, ListView):
    """
    Lista todos los registros de comidas del usuario autenticado.
    Equivalente a EnvioListView en Encomiendas.
    """
    model = RegistroComida
    template_name = "nutricion/lista_registros.html"
    context_object_name = "registros"
    paginate_by = 10

    def get_queryset(self):
        return (
            RegistroComida.objects.filter(usuario=self.request.user)
            .ultima_semana()
            .con_items()
        )


# =========================
# CREAR REGISTRO (CBV)
# =========================
class RegistroCreateView(LoginRequiredMixin, CreateView):
    """
    Crea un nuevo RegistroComida vinculado al usuario autenticado.
    Equivalente a EnvioCreateView en Encomiendas.
    """
    model = RegistroComida
    fields = ["fecha", "tipo_comida"]
    template_name = "nutricion/form_comida.html"
    success_url = reverse_lazy("nutricion:lista_comidas")

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)


# =========================
# CREAR HÁBITO (CBV)
# =========================
class HabitoCreateView(LoginRequiredMixin, CreateView):
    """
    Crea un nuevo RegistroHabito vinculado al usuario autenticado.
    Equivalente a HistorialEstadoCreateView en Encomiendas.
    """
    model = RegistroHabito
    form_class = RegistroHabitoForm
    template_name = "nutricion/form_habito.html"
    success_url = reverse_lazy("nutricion:lista_habitos")

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)


# =========================
# ACTUALIZAR PERFIL (CBV)
# =========================
class PerfilUpdateView(LoginRequiredMixin, UpdateView):
    """
    Actualiza el PerfilUsuario del usuario autenticado.
    Equivalente a ClienteUpdateView en Encomiendas.
    """
    model = PerfilUsuario
    form_class = PerfilForm
    template_name = "nutricion/perfil.html"
    success_url = reverse_lazy("nutricion:perfil")

    def get_object(self, queryset=None):
        """Siempre edita el perfil del usuario autenticado."""
        obj, _ = PerfilUsuario.objects.get_or_create(
            usuario=self.request.user,
            defaults={
                "peso_kg": 70,
                "talla_cm": 170,
                "edad": 25,
                "sexo": "M",
                "nivel_actividad": "SE",
                "objetivo": "MA",
            },
        )
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["editing"] = True
        context["user"] = self.request.user
        return context
