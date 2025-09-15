# Web aplikacija za upravljanje kućnim budžetom

Ova aplikacija omogućuje korisnicima praćenje prihoda i troškova, kategorizaciju transakcija te postavljanje i praćenje ciljeva štednje.

## Funkcionalnosti  

Osnovne mogucnosti  
- Pracenje prihoda i troskova - Evidencija svih financijskih transakcija  
- Kategorizacija transakcija - Organizacija troskova po kategorijama  
- Postavljanje i pracenje ciljeva stednje - Evidencija napretka prema financijskim ciljevima  
- Vizualizacija financijskih podataka - Interaktivni grafikoni i dijagrami  
- Vise racuna/portfelja - Upravljanje razlicitim racunima (gotovina, banka, kreditne kartice)  
- Upravljanje budzetom - Postavljanje mjesecnih, kvartalnih ili godisnjih budzeta po kategoriji  
- Analiza budzet vs stvarnost - Usporedba planiranih i stvarnih troskova  
- Ponavljajuce transakcije - Automatizacija redovitih uplata (place, racuni)  
- Poboljsana nadzorna ploca - Sveobuhvatan pregled sa statusom budzeta  
- Pracenje stanja racuna - Azuriranja stanja u stvarnom vremenu  
- Upozorenja o budzetu - Vizualna upozorenja kod prekomjerne potrosnje  


Pokretanje

#1. Preuzimanje projekta
Preuzmite projekt na svoje računalo i otvorite CMD u direktoriju projekta.

#2. Instalacija Pythona
Potrebna je verzija **Python 3.10+**.  

#3. Kreiranje virtualnog okruženja
cd Desktop\budzet-projekt
py -m venv .venv
.venv\Scripts\activate


#4. Instalacija potrebnih paketa
pip install -r requirements.txt

Ako `requirements.txt` ne postoji, dovoljno je:
pip install django psycopg2-binary


#5. Migracije baze
py manage.py migrate


#6. Kreiranje administratorskog korisnika
py manage.py createsuperuser

Unesesete korisničko ime, email i lozinku.  

#7. Pokretanje servera
py manage.py runserver

#8. Otvaranje u browseru
Otvorite u pregledniku:  
http://127.0.0.1:8000/



 Svaki put kad otvorite novi CMD, potrebno je ponoviti:
  1. cd Desktop\budzet-projekt  
  2. .venv\Scripts\activate
  3. py manage.py runserver