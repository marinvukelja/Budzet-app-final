from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Racun, Kategorija, Transakcija, CiljStednje
from decimal import Decimal
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Kreira demo podatke za aplikaciju'

    def handle(self, *args, **options):
        self.stdout.write('Kreiranje demo podataka...')
        
        # Kreiranje demo korisnika
        demo_user, created = User.objects.get_or_create(
            username='demo',
            defaults={
                'email': 'demo@example.com',
                'first_name': 'Demo',
                'last_name': 'Korisnik'
            }
        )
        if created:
            demo_user.set_password('demo123')
            demo_user.save()
            self.stdout.write('✓ Kreiran demo korisnik (username: demo, password: demo123)')
        else:
            self.stdout.write('✓ Demo korisnik već postoji')
        
        # Kreiranje računa
        racuni_data = [
            {'naziv': 'Gotovina', 'tip': 'GOTOVINA', 'stanje': 5000.00},
            {'naziv': 'Tekući račun', 'tip': 'BANKA', 'stanje': 15000.00},
            {'naziv': 'Štednja', 'tip': 'STEDNJA', 'stanje': 25000.00},
            {'naziv': 'Kreditna kartica', 'tip': 'KREDITNA', 'stanje': -2000.00},
        ]
        
        racuni = []
        for racun_data in racuni_data:
            racun, created = Racun.objects.get_or_create(
                naziv=racun_data['naziv'],
                korisnik=demo_user,
                defaults={
                    'tip': racun_data['tip'],
                    'pocetno_stanje': Decimal(str(racun_data['stanje'])),
                    'trenutno_stanje': Decimal(str(racun_data['stanje']))
                }
            )
            racuni.append(racun)
            if created:
                self.stdout.write(f'✓ Kreiran račun: {racun.naziv}')
        
        # Kreiranje kategorija
        kategorije_data = [
            {'naziv': 'Hrana', 'tip': 'TROSAK'},
            {'naziv': 'Transport', 'tip': 'TROSAK'},
            {'naziv': 'Zabava', 'tip': 'TROSAK'},
            {'naziv': 'Zdravlje', 'tip': 'TROSAK'},
            {'naziv': 'Obrazovanje', 'tip': 'TROSAK'},
            {'naziv': 'Plaća', 'tip': 'PRIHOD'},
            {'naziv': 'Freelance', 'tip': 'PRIHOD'},
            {'naziv': 'Investicije', 'tip': 'PRIHOD'},
        ]
        
        kategorije = []
        for kat_data in kategorije_data:
            kategorija, created = Kategorija.objects.get_or_create(
                naziv=kat_data['naziv'],
                korisnik=demo_user,
                tip=kat_data['tip'],
                defaults={}
            )
            kategorije.append(kategorija)
            if created:
                self.stdout.write(f'✓ Kreirana kategorija: {kategorija.naziv}')
        
        # Kreiranje transakcija za posljednja 3 mjeseca
        self.stdout.write('Kreiranje transakcija...')
        
        # Prihodi
        prihodi_kategorije = [k for k in kategorije if k.tip == 'PRIHOD']
        for i in range(12):  # 12 prihoda (4 mjeseca x 3 prihoda)
            datum = date.today() - timedelta(days=random.randint(1, 90))
            kategorija = random.choice(prihodi_kategorije)
            racun = random.choice(racuni[:2])  # Gotovina ili tekući
            
            iznos = Decimal(str(random.uniform(2000, 8000)))
            opis = f"{kategorija.naziv} - {datum.strftime('%B %Y')}"
            
            transakcija, created = Transakcija.objects.get_or_create(
                opis=opis,
                korisnik=demo_user,
                defaults={
                    'iznos': iznos,
                    'datum': datum,
                    'kategorija': kategorija,
                    'racun': racun
                }
            )
            if created:
                self.stdout.write(f'✓ Kreirana transakcija: {opis} - {iznos}€')
        
        # Troškovi
        trosci_kategorije = [k for k in kategorije if k.tip == 'TROSAK']
        for i in range(50):  # 50 troškova
            datum = date.today() - timedelta(days=random.randint(1, 90))
            kategorija = random.choice(trosci_kategorije)
            racun = random.choice(racuni)
            
            # Različiti iznosi ovisno o kategoriji
            if kategorija.naziv == 'Hrana':
                iznos = Decimal(str(random.uniform(20, 150)))
            elif kategorija.naziv == 'Transport':
                iznos = Decimal(str(random.uniform(10, 100)))
            elif kategorija.naziv == 'Zabava':
                iznos = Decimal(str(random.uniform(30, 200)))
            elif kategorija.naziv == 'Zdravlje':
                iznos = Decimal(str(random.uniform(50, 300)))
            elif kategorija.naziv == 'Obrazovanje':
                iznos = Decimal(str(random.uniform(100, 500)))
            else:
                iznos = Decimal(str(random.uniform(20, 200)))
            
            opisi = {
                'Hrana': ['Kupovina u trgovini', 'Restoran', 'Dostava hrane', 'Kava'],
                'Transport': ['Benzin', 'Javni prijevoz', 'Taksi', 'Parking'],
                'Zabava': ['Kino', 'Koncert', 'Izlazak', 'Video igre'],
                'Zdravlje': ['Liječnik', 'Lijekovi', 'Terapija', 'Pregled'],
                'Obrazovanje': ['Knjige', 'Kurs', 'Seminari', 'Materijali']
            }
            
            opis = random.choice(opisi.get(kategorija.naziv, [kategorija.naziv]))
            
            transakcija, created = Transakcija.objects.get_or_create(
                opis=opis,
                korisnik=demo_user,
                defaults={
                    'iznos': iznos,
                    'datum': datum,
                    'kategorija': kategorija,
                    'racun': racun
                }
            )
            if created:
                self.stdout.write(f'✓ Kreirana transakcija: {opis} - {iznos}€')
        
        # Kreiranje ciljeva štednje
        ciljevi_data = [
            {'naziv': 'Novi laptop', 'cilj_iznos': 2000.00, 'trenutno_stanje': 800.00},
            {'naziv': 'Ljetovanje', 'cilj_iznos': 3000.00, 'trenutno_stanje': 1200.00},
            {'naziv': 'Hitni fond', 'cilj_iznos': 5000.00, 'trenutno_stanje': 2500.00},
        ]
        
        for cilj_data in ciljevi_data:
            cilj, created = CiljStednje.objects.get_or_create(
                naziv=cilj_data['naziv'],
                korisnik=demo_user,
                defaults={
                    'cilj_iznos': Decimal(str(cilj_data['cilj_iznos'])),
                    'trenutno_stanje': Decimal(str(cilj_data['trenutno_stanje'])),
                    'datum_pocetka': date.today() - timedelta(days=random.randint(30, 180)),
                    'datum_kraja': date.today() + timedelta(days=random.randint(30, 365))
                }
            )
            if created:
                self.stdout.write(f'✓ Kreiran cilj: {cilj.naziv}')
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n🎉 Demo podaci uspješno kreirani!\n'
                'Prijavite se s:\n'
                'Username: demo\n'
                'Password: demo123\n'
                'URL: http://127.0.0.1:8000/'
            )
        )
