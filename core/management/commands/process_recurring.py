from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import PonavljajucaTransakcija


class Command(BaseCommand):
    help = 'Obrađuje ponavljajuće transakcije koje su dospjele'

    def handle(self, *args, **options):
        today = timezone.now().date()
        recurring_transactions = PonavljajucaTransakcija.objects.filter(
            aktivno=True,
            sljedeci_datum__lte=today
        )
        
        processed_count = 0
        for recurring in recurring_transactions:
            if not recurring.datum_kraja or recurring.sljedeci_datum <= recurring.datum_kraja:
                recurring.create_transaction()
                processed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Obrađena transakcija: {recurring.opis} - {recurring.iznos} kn'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Ukupno obrađeno {processed_count} ponavljajućih transakcija.')
        )
