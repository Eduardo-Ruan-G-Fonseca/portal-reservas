# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from .models import Voo, Reserva
# import json

# def lista_voos(request):
#     voos = list(Voo.objects.all().values())
#     return JsonResponse(voos, safe=False)

# def detalhe_voo(request, id):
#     try:
#         voo = Voo.objects.values().get(id=id)
#         return JsonResponse(voo)
#     except Voo.DoesNotExist:
#         return JsonResponse({"erro": "Voo não encontrado"}, status=404)

# @csrf_exempt
# def criar_reserva(request):
#     if request.method != 'POST':
#         return JsonResponse({"erro": "Método não permitido"}, status=405)

#     dados = json.loads(request.body)

#     try:
#         voo = Voo.objects.get(id=dados["voo_id"])
#     except:
#         return JsonResponse({"erro": "Voo inválido"}, status=400)

#     reserva = Reserva.objects.create(
#         voo=voo,
#         nome_cliente=dados["nome"],
#         cpf=dados["cpf"]
#     )

#     return JsonResponse({"mensagem": "Reserva criada com sucesso", "id": reserva.id}, status=201)

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .models import Voo, Reserva, Cliente, Assento
from django.utils.crypto import get_random_string


# ---- já devem existir, mas deixo aqui como referência ----

def lista_voos(request):
    voos = Voo.objects.all().order_by("partida")
    data = [
        {
            "id": v.id,
            "numero": v.numero,
            "companhia_id": v.companhia_id,
            "origem_id": v.origem_id,
            "destino_id": v.destino_id,
            "partida": v.partida,
            "chegada": v.chegada,
            "preco_base": str(v.preco_base),
            "status": v.status,
        }
        for v in voos
    ]
    return JsonResponse(data, safe=False)


def detalhe_voo(request, id):
    try:
        v = Voo.objects.get(id=id)
    except Voo.DoesNotExist:
        return JsonResponse({"detail": "Voo não encontrado"}, status=404)

    data = {
        "id": v.id,
        "numero": v.numero,
        "companhia_id": v.companhia_id,
        "origem_id": v.origem_id,
        "destino_id": v.destino_id,
        "partida": v.partida,
        "chegada": v.chegada,
        "preco_base": str(v.preco_base),
        "status": v.status,
    }
    return JsonResponse(data)


@csrf_exempt
def criar_reserva(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Método não permitido"}, status=405)

    data = json.loads(request.body or "{}")

    voo_id = data.get("voo_id")
    nome = data.get("nome")
    cpf = data.get("cpf")

    if not all([voo_id, nome, cpf]):
        return JsonResponse({"detail": "Dados obrigatórios faltando"}, status=400)

    try:
        voo = Voo.objects.get(id=voo_id)
    except Voo.DoesNotExist:
        return JsonResponse({"detail": "Voo não encontrado"}, status=404)

    # cliente pelo cpf (cria se não existir)
    cliente, _ = Cliente.objects.get_or_create(
        cpf=cpf,
        defaults={"nome": nome, "email": f"{cpf}@exemplo.com"},
    )

    # pega um assento qualquer livre (pra não complicar)
    assento_livre = Assento.objects.filter(voo=voo, reserva__isnull=True).first()
    if not assento_livre:
        return JsonResponse({"detail": "Não há assentos disponíveis"}, status=400)

    localizador = get_random_string(6).upper()

    Reserva.objects.create(
        cliente=cliente,
        assento=assento_livre,
        localizador=localizador,
    )

    return JsonResponse(
        {
            "detail": "Reserva criada com sucesso",
            "localizador": localizador,
            "assento": assento_livre.codigo,
        },
        status=201,
    )


# ---- NOVOS ENDPOINTS: SIGNUP E LOGIN PARA O ANGULAR ----

@csrf_exempt
def api_signup(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Método não permitido"}, status=405)

    data = json.loads(request.body or "{}")
    nome = data.get("nome")
    email = data.get("email")
    cpf = data.get("cpf")
    senha = data.get("senha")

    if not all([nome, email, cpf, senha]):
        return JsonResponse({"detail": "Preencha todos os campos"}, status=400)

    if User.objects.filter(username=cpf).exists():
        return JsonResponse({"detail": "Já existe usuário com esse CPF"}, status=400)

    if Cliente.objects.filter(cpf=cpf).exists():
        return JsonResponse({"detail": "Já existe cliente com esse CPF"}, status=400)

    # cria usuário do Django (login) usando CPF como username
    user = User.objects.create_user(
        username=cpf,
        email=email,
        password=senha,
        first_name=nome,
    )

    # cria cliente
    Cliente.objects.create(
        nome=nome,
        email=email,
        cpf=cpf,
    )

    return JsonResponse({"detail": "Cadastro realizado com sucesso"}, status=201)


@csrf_exempt
def api_login(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Método não permitido"}, status=405)

    data = json.loads(request.body or "{}")
    cpf = data.get("cpf")
    senha = data.get("senha")

    if not all([cpf, senha]):
        return JsonResponse({"detail": "Informe CPF e senha"}, status=400)

    user = authenticate(request, username=cpf, password=senha)
    if user is None:
        return JsonResponse({"detail": "CPF ou senha inválidos"}, status=400)

    # login de sessão normal (cookie) – suficiente pro trabalho
    login(request, user)
    return JsonResponse({"detail": "Login realizado com sucesso"}, status=200)

