from datetime import timedelta, date
import calendar
import csv

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import RegisterForm, KategorijaForm, TransakcijaForm, CiljForm, RacunForm, BudzetForm, PonavljajucaTransakcijaForm
from .models import Kategorija, Transakcija, CiljStednje, Racun, Budzet, PonavljajucaTransakcija


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "core/register.html", {"form": form})


class MyLoginView(LoginView):
    template_name = "core/login.html"


class MyLogoutView(LogoutView):
    next_page = "login"


@login_required
def dashboard(request):
    today = timezone.localdate()

    # cijeli tekući mjesec
    first_of_month = date(today.year, today.month, 1)
    last_day = calendar.monthrange(today.year, today.month)[1]
    end_of_month = date(today.year, today.month, last_day)

    trans = Transakcija.objects.filter(
        korisnik=request.user,
        datum__gte=first_of_month,
        datum__lte=end_of_month
    )

    prihodi_val = trans.filter(kategorija__tip="PRIHOD").aggregate(s=Sum("iznos"))["s"] or 0
    troskovi_val = trans.filter(kategorija__tip="TROSAK").aggregate(s=Sum("iznos"))["s"] or 0

    prihodi = float(prihodi_val)
    troskovi = abs(float(troskovi_val))
    stanje = prihodi - troskovi

    # PIE graf
    pie_qs = (trans.filter(kategorija__tip="TROSAK")
                    .values("kategorija__naziv")
                    .annotate(total=Sum("iznos"))
                    .order_by("-total"))
    pie_labels = [x["kategorija__naziv"] for x in pie_qs]
    pie_values = [abs(float(x["total"])) for x in pie_qs]

    # BAR graf
    year_ago = today.replace(day=1) - timedelta(days=365)
    hist = (Transakcija.objects
            .filter(korisnik=request.user, datum__gte=year_ago, datum__lte=end_of_month)
            .annotate(m=TruncMonth("datum"))
            .values("m", "kategorija__tip")
            .annotate(total=Sum("iznos"))
            .order_by("m"))

    months = []
    inc = {}
    exp = {}
    cur = year_ago.replace(day=1)
    while cur <= end_of_month:
        key = cur.strftime("%Y-%m")
        months.append(key)
        inc[key] = 0.0
        exp[key] = 0.0
        if cur.month == 12:
            cur = cur.replace(year=cur.year + 1, month=1)
        else:
            cur = cur.replace(month=cur.month + 1)

    for row in hist:
        key = row["m"].strftime("%Y-%m")
        val = float(row["total"] or 0)
        if row["kategorija__tip"] == "PRIHOD":
            inc[key] += val
        else:
            exp[key] += val

    bar_labels = [f'{k.split("-")[1]}.{k.split("-")[0]}' for k in months]
    bar_prihodi = [inc[k] for k in months]
    bar_troskovi = [exp[k] for k in months]

    ciljevi = CiljStednje.objects.filter(korisnik=request.user).order_by("naziv")
    
    # Budžet analiza za trenutni mjesec
    current_year = today.year
    current_month = today.month
    budgets = Budzet.objects.filter(
        korisnik=request.user,
        godina=current_year,
        mjesec=current_month,
        aktivno=True
    )
    
    budget_summary = []
    total_budget = 0
    total_spent = 0
    over_budget_count = 0
    
    for budget in budgets:
        actual_spending = budget.get_actual_spending()
        remaining = budget.get_remaining_budget()
        percentage_used = budget.get_percentage_used()
        
        budget_summary.append({
            'budget': budget,
            'actual': actual_spending,
            'remaining': remaining,
            'percentage': percentage_used,
            'status': 'over' if remaining < 0 else 'warning' if percentage_used > 80 else 'under'
        })
        
        total_budget += float(budget.iznos)
        total_spent += actual_spending
        if remaining < 0:
            over_budget_count += 1
    
    # Računi
    racuni = Racun.objects.filter(korisnik=request.user, aktivno=True)
    total_account_balance = sum(float(racun.trenutno_stanje) for racun in racuni)
    
    # Ponavljajuće transakcije
    recurring_count = PonavljajucaTransakcija.objects.filter(
        korisnik=request.user, 
        aktivno=True
    ).count()
    
    return render(request, "core/dashboard.html", {
        "prihodi": prihodi, "troskovi": troskovi, "stanje": stanje,
        "pie_labels": pie_labels, "pie_values": pie_values,
        "bar_labels": bar_labels, "bar_prihodi": bar_prihodi, "bar_troskovi": bar_troskovi,
        "ciljevi": ciljevi,
        "budget_summary": budget_summary,
        "total_budget": total_budget,
        "total_spent": total_spent,
        "over_budget_count": over_budget_count,
        "racuni": racuni,
        "total_account_balance": total_account_balance,
        "recurring_count": recurring_count,
        "current_month": current_month,
        "current_year": current_year
    })


@login_required
def kategorije_list_create(request):
    if request.method == "POST":
        form = KategorijaForm(request.POST)
        if form.is_valid():
            kat = form.save(commit=False)
            kat.korisnik = request.user
            kat.save()
            return redirect("kategorije")
    else:
        form = KategorijaForm()
    items = Kategorija.objects.filter(korisnik=request.user)
    return render(request, "core/kategorije.html", {"form": form, "items": items})


@login_required
def transakcije_list_create(request):
    qs = Transakcija.objects.filter(korisnik=request.user)

    tip = request.GET.get("tip")
    kategorija_id = request.GET.get("kategorija")
    od = request.GET.get("od")
    do = request.GET.get("do")

    if tip in ("PRIHOD", "TROSAK"):
        qs = qs.filter(kategorija__tip=tip)
    if kategorija_id:
        qs = qs.filter(kategorija_id=kategorija_id)
    if od:
        qs = qs.filter(datum__gte=od)
    if do:
        qs = qs.filter(datum__lte=do)

    if request.method == "POST":
        form = TransakcijaForm(request.POST)
        form.fields["kategorija"].queryset = Kategorija.objects.filter(korisnik=request.user)
        form.fields["racun"].queryset = Racun.objects.filter(korisnik=request.user, aktivno=True)
        form.fields["doprinos_cilju"].queryset = CiljStednje.objects.filter(korisnik=request.user)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.korisnik = request.user
            obj.save()
            return redirect("transakcije")
    else:
        form = TransakcijaForm()
        form.fields["kategorija"].queryset = Kategorija.objects.filter(korisnik=request.user)
        form.fields["racun"].queryset = Racun.objects.filter(korisnik=request.user, aktivno=True)
        form.fields["doprinos_cilju"].queryset = CiljStednje.objects.filter(korisnik=request.user)

    kategorije = Kategorija.objects.filter(korisnik=request.user)
    return render(request, "core/transakcije.html", {"form": form, "items": qs, "kategorije": kategorije})


@login_required
def ciljevi_list_create(request):
    if request.method == "POST":
        form = CiljForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.korisnik = request.user
            obj.save()
            return redirect("ciljevi")
    else:
        form = CiljForm()
    items = CiljStednje.objects.filter(korisnik=request.user)
    return render(request, "core/ciljevi.html", {"form": form, "items": items})


@login_required
def transakcije_export_csv(request):
    qs = Transakcija.objects.filter(korisnik=request.user)

    tip = request.GET.get("tip")
    kategorija_id = request.GET.get("kategorija")
    od = request.GET.get("od")
    do = request.GET.get("do")

    if tip in ("PRIHOD", "TROSAK"):
        qs = qs.filter(kategorija__tip=tip)
    if kategorija_id:
        qs = qs.filter(kategorija_id=kategorija_id)
    if od:
        qs = qs.filter(datum__gte=od)
    if do:
        qs = qs.filter(datum__lte=do)

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="transakcije.csv"'
    writer = csv.writer(response)
    writer.writerow(["Datum", "Tip", "Kategorija", "Iznos", "Opis", "Cilj"])
    for t in qs.order_by("-datum", "-id"):
        writer.writerow([
            t.datum,
            t.kategorija.get_tip_display(),
            t.kategorija.naziv,
            float(t.iznos),
            t.opis or "",
            t.doprinos_cilju.naziv if t.doprinos_cilju else ""
        ])
    return response

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect("login")


# Novi view-ovi za poboljšanja

@login_required
def racuni_list_create(request):
    if request.method == "POST":
        form = RacunForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.korisnik = request.user
            obj.trenutno_stanje = obj.pocetno_stanje
            obj.save()
            return redirect("racuni")
    else:
        form = RacunForm()
    items = Racun.objects.filter(korisnik=request.user)
    return render(request, "core/racuni.html", {"form": form, "items": items})


@login_required
def budzeti_list_create(request):
    if request.method == "POST":
        form = BudzetForm(request.POST, user=request.user)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.korisnik = request.user
            obj.save()
            return redirect("budzeti")
    else:
        form = BudzetForm(user=request.user)
    items = Budzet.objects.filter(korisnik=request.user)
    return render(request, "core/budzeti.html", {"form": form, "items": items})


@login_required
def ponavljajuce_transakcije_list_create(request):
    if request.method == "POST":
        form = PonavljajucaTransakcijaForm(request.POST, user=request.user)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.korisnik = request.user
            obj.sljedeci_datum = obj.datum_pocetka
            obj.save()
            return redirect("ponavljajuce")
    else:
        form = PonavljajucaTransakcijaForm(user=request.user)
    items = PonavljajucaTransakcija.objects.filter(korisnik=request.user)
    return render(request, "core/ponavljajuce.html", {"form": form, "items": items})


@login_required
def process_recurring_transactions(request):
    """Obrađuje ponavljajuće transakcije koje su dospjele"""
    today = timezone.now().date()
    recurring_transactions = PonavljajucaTransakcija.objects.filter(
        korisnik=request.user,
        aktivno=True,
        sljedeci_datum__lte=today
    )
    
    processed_count = 0
    for recurring in recurring_transactions:
        if not recurring.datum_kraja or recurring.sljedeci_datum <= recurring.datum_kraja:
            recurring.create_transaction()
            processed_count += 1
    
    return HttpResponse(f"Obrađeno {processed_count} ponavljajućih transakcija.")


@login_required
def budget_analysis(request):
    """Analiza budžeta vs stvarnih troškova"""
    today = timezone.now().date()
    current_year = today.year
    current_month = today.month
    
    # Dohvati sve aktivne budžete za trenutnu godinu
    budgets = Budzet.objects.filter(
        korisnik=request.user,
        godina=current_year,
        aktivno=True
    ).order_by('period', 'mjesec', 'kategorija__naziv')
    
    # Grupiraj budžete po kategoriji
    budget_groups = {}
    for budget in budgets:
        kategorija_naziv = budget.kategorija.naziv
        if kategorija_naziv not in budget_groups:
            budget_groups[kategorija_naziv] = {
                'kategorija': budget.kategorija,
                'total_budget': 0,
                'total_actual': 0,
                'budgets': []
            }
        
        actual_spending = budget.get_actual_spending()
        budget_groups[kategorija_naziv]['total_budget'] += float(budget.iznos)
        budget_groups[kategorija_naziv]['total_actual'] += actual_spending
        budget_groups[kategorija_naziv]['budgets'].append(budget)
    
    # Kreiraj budget_data za prikaz
    budget_data = []
    for kategorija_naziv, group in budget_groups.items():
        total_remaining = group['total_budget'] - group['total_actual']
        percentage_used = (group['total_actual'] / group['total_budget'] * 100) if group['total_budget'] > 0 else 0
        
        budget_data.append({
            'kategorija_naziv': kategorija_naziv,
            'kategorija': group['kategorija'],
            'total_budget': group['total_budget'],
            'actual': group['total_actual'],
            'remaining': total_remaining,
            'percentage': percentage_used,
            'status': 'over' if total_remaining < 0 else 'under' if percentage_used < 80 else 'warning',
            'budgets': group['budgets']
        })
    
    return render(request, "core/budget_analysis.html", {
        "budget_data": budget_data,
        "current_month": current_month,
        "current_year": current_year
    })
