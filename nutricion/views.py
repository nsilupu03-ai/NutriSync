# nutricion/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import (
    RegistroComida,
    RegistroHabito,
    ItemRegistro,
    Logro,
    LogroUsuario,
    MetaNutricional,
    PerfilUsuario,
)
from .forms import ItemRegistroForm


# =========================
# DASHBOARD
# =========================
@login_required
def dashboard(request):
    """
    Vista principal: muestra totales del día (calorías, macros),
    progreso vs meta nutricional y hábitos del día.
    """
    hoy = timezone.now().date()
    usuario = request.user

    # Registros de comida de hoy con sus ítems
    registros_hoy = (
        RegistroComida.objects.filter(usuario=usuario, fecha=hoy)
        .con_items()
    )

    # Totales del día
    total_calorias = sum(r.total_calorias for r in registros_hoy)
    total_proteinas = sum(
        sum(item.total_proteinas for item in r.items.all()) for r in registros_hoy
    )
    total_carbohidratos = sum(
        sum(item.total_carbohidratos for item in r.items.all()) for r in registros_hoy
    )
    total_grasas = sum(
        sum(item.total_grasas for item in r.items.all()) for r in registros_hoy
    )

    # Meta nutricional (puede no existir)
    meta = None
    calorias_meta = 2000  # valor por defecto
    porcentaje = 0
    try:
        perfil = usuario.perfil
        calorias_meta = perfil.harris_benedict
        try:
            meta = perfil.metas.latest("id")
            calorias_meta = meta.calorias_meta
        except MetaNutricional.DoesNotExist:
            pass
    except PerfilUsuario.DoesNotExist:
        pass

    if calorias_meta > 0:
        porcentaje = min(int((float(total_calorias) / float(calorias_meta)) * 100), 100)

    alerta_calorias = float(total_calorias) > (float(calorias_meta) * 1.10)

    # Hábito de hoy
    habito_hoy = RegistroHabito.objects.filter(usuario=usuario, fecha=hoy).first()

    # Logros obtenidos
    logros_obtenidos = LogroUsuario.objects.filter(usuario=usuario).count()

    context = {
        "registros_hoy": registros_hoy,
        "total_calorias": total_calorias,
        "total_proteinas": total_proteinas,
        "total_carbohidratos": total_carbohidratos,
        "total_grasas": total_grasas,
        "calorias_meta": calorias_meta,
        "porcentaje": porcentaje,
        "alerta_calorias": alerta_calorias,
        "habito_hoy": habito_hoy,
        "logros_obtenidos": logros_obtenidos,
        "hoy": hoy,
    }
    return render(request, "nutricion/dashboard.html", context)


# =========================
# LISTA COMIDAS
# =========================
@login_required
def lista_comidas(request):
    """Lista todos los registros de comidas del usuario (última semana)."""
    registros = (
        RegistroComida.objects.filter(usuario=request.user)
        .ultima_semana()
        .con_items()
    )
    return render(request, "nutricion/lista_registros.html", {"registros": registros})


# =========================
# CREAR COMIDA
# =========================
@login_required
def crear_comida(request):
    """
    Crea un RegistroComida para hoy (tipo_comida elegido)
    y añade un ItemRegistro al registro.
    """
    hoy = timezone.now().date()

    if request.method == "POST":
        tipo_comida = request.POST.get("tipo_comida")
        form = ItemRegistroForm(request.POST)

        if form.is_valid() and tipo_comida:
            # Obtener o crear el registro del día
            registro, _ = RegistroComida.objects.get_or_create(
                usuario=request.user,
                fecha=hoy,
                tipo_comida=tipo_comida,
            )
            item = form.save(commit=False)
            item.registro = registro
            item.save()
            messages.success(request, "Alimento registrado correctamente.")
            return redirect("nutricion:lista_comidas")
        else:
            messages.error(request, "Corrige los errores del formulario.")
    else:
        form = ItemRegistroForm()

    from config.choices import TipoComida
    context = {
        "form": form,
        "tipo_comida_choices": TipoComida.choices,
        "hoy": hoy,
    }
    return render(request, "nutricion/form_comida.html", context)


# =========================
# LISTA HÁBITOS
# =========================
@login_required
def lista_habitos(request):
    """Lista los hábitos del usuario en la última semana."""
    habitos = (
        RegistroHabito.objects.filter(usuario=request.user)
        .ultima_semana()
        .order_by("-fecha")
    )
    return render(request, "nutricion/lista_habitos.html", {"habitos": habitos})


# =========================
# LOGROS
# =========================
@login_required
def logros_view(request):
    """
    Muestra todos los logros separados en:
    - obtenidos (LogroUsuario del usuario)
    - bloqueados (el resto)
    """
    todos_logros = Logro.objects.all()
    ids_obtenidos = LogroUsuario.objects.filter(
        usuario=request.user
    ).values_list("logro_id", flat=True)

    obtenidos = todos_logros.filter(id__in=ids_obtenidos)
    bloqueados = todos_logros.exclude(id__in=ids_obtenidos)

    context = {
        "obtenidos": obtenidos,
        "bloqueados": bloqueados,
    }
    return render(request, "nutricion/logros.html", context)
