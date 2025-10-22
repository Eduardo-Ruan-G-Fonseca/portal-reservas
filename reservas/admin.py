from django.contrib import admin
from .models import Cliente, Aeroporto, CompanhiaAerea, Voo, Assento, Reserva

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "cpf")
    search_fields = ("nome", "email", "cpf")

@admin.register(Aeroporto)
class AeroportoAdmin(admin.ModelAdmin):
    list_display = ("codigo_iata", "nome", "cidade", "uf")
    search_fields = ("codigo_iata", "nome", "cidade", "uf")
    list_filter = ("uf",)

@admin.register(CompanhiaAerea)
class CompanhiaAereaAdmin(admin.ModelAdmin):
    list_display = ("nome", "codigo")
    search_fields = ("nome", "codigo")

class AssentoInline(admin.TabularInline):
    model = Assento
    extra = 5
    fields = ("codigo", "classe")
    show_change_link = True

@admin.register(Voo)
class VooAdmin(admin.ModelAdmin):
    list_display = ("numero","companhia","origem","destino","partida","chegada","status","preco_base")
    search_fields = ("numero","companhia__nome","origem__codigo_iata","destino__codigo_iata")
    list_filter = ("status","companhia","origem","destino")
    date_hierarchy = "partida"
    inlines = [AssentoInline]

@admin.register(Assento)
class AssentoAdmin(admin.ModelAdmin):
    list_display = ("voo","codigo","classe")
    search_fields = ("voo__numero","codigo")
    list_filter = ("classe","voo__companhia")

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("localizador","cliente","assento","status","criado_em")
    search_fields = ("localizador","cliente__nome","cliente__cpf","assento__voo__numero")
    list_filter = ("status","assento__voo__companhia","assento__voo__origem","assento__voo__destino")
