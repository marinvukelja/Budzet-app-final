from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import calendar

class Kategorija(models.Model):
    TIP_CHOICES = (("PRIHOD", "Prihod"), ("TROSAK", "Trošak"))
    korisnik = models.ForeignKey(User, on_delete=models.CASCADE)
    naziv = models.CharField(max_length=100)
    tip = models.CharField(max_length=10, choices=TIP_CHOICES)

    class Meta:
        unique_together = ("korisnik", "naziv", "tip")
        ordering = ["naziv"]

    def __str__(self):
        return f"{self.naziv} ({self.tip})"

class CiljStednje(models.Model):
    korisnik = models.ForeignKey(User, on_delete=models.CASCADE)
    naziv = models.CharField(max_length=120)
    cilj_iznos = models.DecimalField(max_digits=12, decimal_places=2)
    trenutno_stanje = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    datum_pocetka = models.DateField()
    datum_kraja = models.DateField(null=True, blank=True)

    def progress(self):
        if self.cilj_iznos and self.cilj_iznos > 0:
            return float((self.trenutno_stanje / self.cilj_iznos) * 100)
        return 0.0

    def __str__(self):
        return self.naziv

class Racun(models.Model):
    TIP_CHOICES = (
        ("GOTOVINA", "Gotovina"),
        ("BANKA", "Banka"),
        ("KREDITNA", "Kreditna kartica"),
        ("STEDNJA", "Štednja"),
        ("OSTALO", "Ostalo")
    )
    korisnik = models.ForeignKey(User, on_delete=models.CASCADE)
    naziv = models.CharField(max_length=100)
    tip = models.CharField(max_length=10, choices=TIP_CHOICES)
    pocetno_stanje = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    trenutno_stanje = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    aktivno = models.BooleanField(default=True)
    datum_kreiranja = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("korisnik", "naziv")
        ordering = ["naziv"]

    def __str__(self):
        return f"{self.naziv} ({self.get_tip_display()})"

    def update_balance(self):
        """Ažurira trenutno stanje računa na temelju transakcija"""
        from django.db.models import Sum
        from decimal import Decimal
        prihodi = self.transakcije.filter(kategorija__tip="PRIHOD").aggregate(
            total=Sum('iznos'))['total'] or Decimal('0')
        troskovi = self.transakcije.filter(kategorija__tip="TROSAK").aggregate(
            total=Sum('iznos'))['total'] or Decimal('0')
        self.trenutno_stanje = self.pocetno_stanje + Decimal(str(prihodi)) - abs(Decimal(str(troskovi)))
        self.save()

class Budzet(models.Model):
    PERIOD_CHOICES = (
        ("MJESEC", "Mjesečni"),
        ("KVARTAL", "Kvartalni"),
        ("GODINA", "Godišnji")
    )
    korisnik = models.ForeignKey(User, on_delete=models.CASCADE)
    kategorija = models.ForeignKey(Kategorija, on_delete=models.CASCADE)
    iznos = models.DecimalField(max_digits=12, decimal_places=2)
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default="MJESEC")
    godina = models.IntegerField()
    mjesec = models.IntegerField(null=True, blank=True)  # null za godišnji budžet
    aktivno = models.BooleanField(default=True)
    datum_kreiranja = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("korisnik", "kategorija", "godina", "mjesec", "period")
        ordering = ["-godina", "-mjesec", "kategorija__naziv"]

    def __str__(self):
        if self.period == "GODINA":
            return f"{self.kategorija.naziv} - {self.godina}"
        elif self.period == "KVARTAL":
            if self.mjesec is None:
                kvartal = 1  # Default prvi kvartal
            else:
                kvartal = ((self.mjesec - 1) // 3) + 1
            return f"{self.kategorija.naziv} - Q{kvartal} {self.godina}"
        else:
            if self.mjesec is None:
                return f"{self.kategorija.naziv} - 1/{self.godina}"  # Default siječanj
            else:
                return f"{self.kategorija.naziv} - {self.mjesec}/{self.godina}"

    def get_actual_spending(self):
        """Vraća stvarni iznos potrošen u tom periodu"""
        from django.db.models import Sum
        from datetime import date
        
        if self.period == "GODINA":
            start_date = date(self.godina, 1, 1)
            end_date = date(self.godina, 12, 31)
        elif self.period == "KVARTAL":
            if self.mjesec is None:
                # Ako je mjesec None za kvartalni budžet, koristi prvi kvartal
                quarter_start = 1
            else:
                quarter_start = ((self.mjesec - 1) // 3) * 3 + 1
            start_date = date(self.godina, quarter_start, 1)
            if quarter_start == 10:
                end_date = date(self.godina, 12, 31)
            else:
                end_date = date(self.godina, quarter_start + 2, calendar.monthrange(self.godina, quarter_start + 2)[1])
        else:  # MJESEC
            if self.mjesec is None:
                # Ako je mjesec None za mjesečni budžet, koristi siječanj
                month = 1
            else:
                month = self.mjesec
            start_date = date(self.godina, month, 1)
            end_date = date(self.godina, month, calendar.monthrange(self.godina, month)[1])
        
        actual = Transakcija.objects.filter(
            korisnik=self.korisnik,
            kategorija=self.kategorija,
            datum__gte=start_date,
            datum__lte=end_date
        ).aggregate(total=Sum('iznos'))['total'] or 0
        
        return abs(float(actual))

    def get_remaining_budget(self):
        """Vraća preostali budžet"""
        return float(self.iznos) - self.get_actual_spending()

    def get_percentage_used(self):
        """Vraća postotak iskorištenog budžeta"""
        if self.iznos > 0:
            return (self.get_actual_spending() / float(self.iznos)) * 100
        return 0

class PonavljajucaTransakcija(models.Model):
    FREQUENCY_CHOICES = (
        ("DNEVNO", "Dnevno"),
        ("TJEDNO", "Tjedno"),
        ("MJESECNO", "Mjesečno"),
        ("KVARTALNO", "Kvartalno"),
        ("GODISNJE", "Godišnje")
    )
    korisnik = models.ForeignKey(User, on_delete=models.CASCADE)
    kategorija = models.ForeignKey(Kategorija, on_delete=models.CASCADE)
    iznos = models.DecimalField(max_digits=12, decimal_places=2)
    opis = models.CharField(max_length=255)
    frekvencija = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    datum_pocetka = models.DateField()
    datum_kraja = models.DateField(null=True, blank=True)
    aktivno = models.BooleanField(default=True)
    sljedeci_datum = models.DateField()
    doprinos_cilju = models.ForeignKey(CiljStednje, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["sljedeci_datum"]

    def __str__(self):
        return f"{self.opis} - {self.iznos} ({self.get_frekvencija_display()})"

    def calculate_next_date(self, current_date):
        """Izračunava sljedeći datum na temelju frekvencije"""
        if self.frekvencija == "DNEVNO":
            return current_date + timedelta(days=1)
        elif self.frekvencija == "TJEDNO":
            return current_date + timedelta(weeks=1)
        elif self.frekvencija == "MJESECNO":
            if current_date.month == 12:
                return current_date.replace(year=current_date.year + 1, month=1)
            else:
                return current_date.replace(month=current_date.month + 1)
        elif self.frekvencija == "KVARTALNO":
            if current_date.month in [1, 2, 3]:
                return current_date.replace(month=4)
            elif current_date.month in [4, 5, 6]:
                return current_date.replace(month=7)
            elif current_date.month in [7, 8, 9]:
                return current_date.replace(month=10)
            else:
                return current_date.replace(year=current_date.year + 1, month=1)
        elif self.frekvencija == "GODISNJE":
            return current_date.replace(year=current_date.year + 1)
        return current_date

    def create_transaction(self):
        """Kreira transakciju i ažurira sljedeći datum"""
        if self.sljedeci_datum <= timezone.now().date():
            Transakcija.objects.create(
                korisnik=self.korisnik,
                kategorija=self.kategorija,
                iznos=self.iznos,
                datum=self.sljedeci_datum,
                opis=self.opis,
                doprinos_cilju=self.doprinos_cilju
            )
            self.sljedeci_datum = self.calculate_next_date(self.sljedeci_datum)
            self.save()

class Transakcija(models.Model):
    korisnik = models.ForeignKey(User, on_delete=models.CASCADE)
    kategorija = models.ForeignKey(Kategorija, on_delete=models.PROTECT)
    racun = models.ForeignKey(Racun, on_delete=models.PROTECT, null=True, blank=True, related_name='transakcije')
    iznos = models.DecimalField(max_digits=12, decimal_places=2)
    datum = models.DateField()
    opis = models.CharField(max_length=255, blank=True)
    doprinos_cilju = models.ForeignKey(CiljStednje, null=True, blank=True, on_delete=models.SET_NULL)
    ponavljajuca = models.ForeignKey(PonavljajucaTransakcija, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["-datum", "-id"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Ažuriraj stanje računa ako je transakcija vezana za račun
        if self.racun:
            self.racun.update_balance()
