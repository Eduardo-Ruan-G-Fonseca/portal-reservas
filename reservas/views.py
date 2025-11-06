from datetime import datetime, timedelta
import random, string

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import SignUpForm, SearchVoosForm, ReservaAssentoForm
from .models import Aeroporto, Voo, Assento, Reserva, Cliente

def _gerar_localizador(tamanho=6):
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(tamanho))

def home(request):
    form = SearchVoosForm(request.GET or None)
    if form.is_valid():
        # se não estiver logado, mostra aviso e fica na home
        if not request.user.is_authenticated:
            messages.warning(request, "Para buscar voos, faça login ou cadastre-se.")
            return render(request, "reservas/home.html", {"form": form})

        origem = form.cleaned_data["origem"].id
        destino = form.cleaned_data["destino"].id
        data = form.cleaned_data["data"].isoformat()
        return redirect(
            reverse("reservas:voos_list") + f"?origem={origem}&destino={destino}&data={data}"
        )
    return render(request, "reservas/home.html", {"form": form})

def voos_list(request):
    form = SearchVoosForm(request.GET or None)
    voos = Voo.objects.none()
    if form.is_valid():
        origem = form.cleaned_data["origem"]
        destino = form.cleaned_data["destino"]
        data = form.cleaned_data["data"]
        inicio = timezone.make_aware(datetime.combine(data, datetime.min.time()))
        fim = timezone.make_aware(datetime.combine(data, datetime.max.time()))
        voos = Voo.objects.filter(
            origem=origem, destino=destino, partida__range=(inicio, fim)
        ).order_by("partida")
    return render(request, "reservas/voos_list.html", {"form": form, "voos": voos})

def voo_detail(request, voo_id:int):
    voo = get_object_or_404(Voo, id=voo_id)
    assentos_disponiveis = voo.assentos.filter(reserva__isnull=True).order_by("codigo")
    return render(request, "reservas/voo_detail.html", {
        "voo": voo,
        "assentos": assentos_disponiveis,
        "form": ReservaAssentoForm(),
    })

@login_required
@transaction.atomic
def reservar_assento(request, assento_id:int):
    if request.method != "POST":
        return HttpResponseForbidden("Método inválido.")
    assento = get_object_or_404(Assento.objects.select_for_update(), id=assento_id)
    if hasattr(assento, "reserva"):
        messages.error(request, "Este assento acabou de ser reservado por outra pessoa.")
        return redirect("reservas:voo_detail", voo_id=assento.voo_id)

    # Localiza o Cliente correspondente ao e-mail do usuário autenticado
    cliente = Cliente.objects.filter(email=request.user.email).first()
    if not cliente:
        # Cria automaticamente mantendo o diagrama original intacto
        cliente = Cliente.objects.create(nome=request.user.get_full_name() or request.user.username,
                                         email=request.user.email,
                                         cpf="")  # CPF em branco caso não tenha sido coletado na criação do User

    # Gera localizador único
    localizador = _gerar_localizador(6)
    while Reserva.objects.filter(localizador=localizador).exists():
        localizador = _gerar_localizador(6)

    reserva = Reserva.objects.create(
        cliente=cliente,
        assento=assento,
        localizador=localizador,
    )
    messages.success(request, f"Reserva confirmada! Localizador: {reserva.localizador}")
    return redirect("reservas:minhas_reservas")

@login_required
def minhas_reservas(request):
    cliente = Cliente.objects.filter(email=request.user.email).first()
    reservas = Reserva.objects.filter(cliente=cliente).select_related("assento__voo","assento__voo__origem","assento__voo__destino") if cliente else []
    return render(request, "reservas/minhas_reservas.html", {"reservas": reservas})

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect("reservas:home")
    else:
        form = SignUpForm()
    return render(request, "reservas/signup.html", {"form": form})