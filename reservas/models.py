from django.db import models
from django.utils import timezone

class Cliente(models.Model):
    nome = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    cpf = models.CharField("CPF", max_length=11, unique=True)
    data_nascimento = models.DateField(null=True, blank=True)
    def __str__(self): return f"{self.nome} ({self.cpf})"

class Aeroporto(models.Model):
    codigo_iata = models.CharField("Código IATA", max_length=3, unique=True)
    nome = models.CharField(max_length=120)
    cidade = models.CharField(max_length=80)
    uf = models.CharField(max_length=2)
    def __str__(self): return f"{self.codigo_iata} - {self.cidade}/{self.uf}"

class CompanhiaAerea(models.Model):
    nome = models.CharField(max_length=120, unique=True)
    codigo = models.CharField("Código (2-3 letras)", max_length=3, unique=True)
    def __str__(self): return f"{self.nome} ({self.codigo})"

class Voo(models.Model):
    class Status(models.TextChoices):
        PROGRAMADO = "PROG", "Programado"
        CANCELADO = "CANC", "Cancelado"
        CONCLUIDO = "CONC", "Concluído"
    numero = models.CharField("Nº do voo", max_length=8)  # ex: JJ3456
    companhia = models.ForeignKey(CompanhiaAerea, on_delete=models.PROTECT, related_name="voos")
    origem = models.ForeignKey(Aeroporto, on_delete=models.PROTECT, related_name="voos_origem")
    destino = models.ForeignKey(Aeroporto, on_delete=models.PROTECT, related_name="voos_destino")
    partida = models.DateTimeField()
    chegada = models.DateTimeField()
    preco_base = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=4, choices=Status.choices, default=Status.PROGRAMADO)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["numero","partida"], name="unique_numero_partida")]
    def __str__(self):
        return f"{self.numero} {self.origem.codigo_iata}->{self.destino.codigo_iata} ({self.partida:%d/%m %H:%M})"

class Assento(models.Model):
    class Classe(models.TextChoices):
        ECONOMICA = "ECO", "Econômica"
        PREMIUM = "PRE", "Premium Economy"
        EXECUTIVA = "EXE", "Executiva"
    voo = models.ForeignKey(Voo, on_delete=models.CASCADE, related_name="assentos")
    codigo = models.CharField("Assento", max_length=5)  # ex: 12A
    classe = models.CharField(max_length=3, choices=Classe.choices, default=Classe.ECONOMICA)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["voo","codigo"], name="unique_assento_por_voo")]
    def __str__(self): return f"{self.voo.numero} - {self.codigo} ({self.get_classe_display()})"

class Reserva(models.Model):
    class Status(models.TextChoices):
        ATIVA = "ATV", "Ativa"
        CANCELADA = "CAN", "Cancelada"
        EMBARCADA = "EMB", "Embarcada"
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="reservas")
    assento = models.OneToOneField(Assento, on_delete=models.PROTECT, related_name="reserva")
    localizador = models.CharField(max_length=8, unique=True)  # ex: 6-8 letras/números
    status = models.CharField(max_length=3, choices=Status.choices, default=Status.ATIVA)
    criado_em = models.DateTimeField(default=timezone.now)
    def __str__(self): return f"{self.localizador} - {self.cliente.nome} - {self.assento}"
