from django.contrib import admin
from .models import Kategorija, Transakcija, CiljStednje, Racun, Budzet, PonavljajucaTransakcija

@admin.register(Kategorija)
class KategorijaAdmin(admin.ModelAdmin):
    list_display = ("naziv", "tip", "korisnik")
    list_filter = ("tip",)
    search_fields = ("naziv",)

@admin.register(Transakcija)
class TransakcijaAdmin(admin.ModelAdmin):
    list_display = ("datum", "kategorija", "racun", "iznos", "korisnik", "doprinos_cilju")
    list_filter = ("kategorija__tip", "kategorija", "racun")
    search_fields = ("opis",)

@admin.register(CiljStednje)
class CiljStednjeAdmin(admin.ModelAdmin):
    list_display = ("naziv", "korisnik", "cilj_iznos", "trenutno_stanje")

@admin.register(Racun)
class RacunAdmin(admin.ModelAdmin):
    list_display = ("naziv", "tip", "korisnik", "trenutno_stanje", "aktivno")
    list_filter = ("tip", "aktivno")
    search_fields = ("naziv",)

@admin.register(Budzet)
class BudzetAdmin(admin.ModelAdmin):
    list_display = ("kategorija", "period", "godina", "mjesec", "iznos", "korisnik", "aktivno")
    list_filter = ("period", "godina", "mjesec", "aktivno")
    search_fields = ("kategorija__naziv",)

@admin.register(PonavljajucaTransakcija)
class PonavljajucaTransakcijaAdmin(admin.ModelAdmin):
    list_display = ("opis", "kategorija", "iznos", "frekvencija", "sljedeci_datum", "korisnik", "aktivno")
    list_filter = ("frekvencija", "aktivno")
    search_fields = ("opis",)
