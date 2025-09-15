from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from .models import Transakcija

@receiver(post_save, sender=Transakcija)
def update_goal_on_save(sender, instance: Transakcija, created, **kwargs):
    if created and instance.doprinos_cilju:
        delta = instance.iznos if instance.kategorija.tip == "PRIHOD" else -instance.iznos
        cilj = instance.doprinos_cilju
        cilj.trenutno_stanje += delta
        cilj.save()
        print(f"Signal: Ažuriran cilj {cilj.naziv} za {delta}€, novo stanje: {cilj.trenutno_stanje}€")

@receiver(pre_save, sender=Transakcija)
def handle_update(sender, instance: Transakcija, **kwargs):
    if not instance.pk:
        return
    try:
        old = Transakcija.objects.get(pk=instance.pk)
    except Transakcija.DoesNotExist:
        return
    # reverzaj stari utjecaj
    if old.doprinos_cilju:
        old_delta = old.iznos if old.kategorija.tip == "PRIHOD" else -old.iznos
        cilj = old.doprinos_cilju
        cilj.trenutno_stanje -= old_delta
        cilj.save()
    # primjeni novi
    if instance.doprinos_cilju:
        new_delta = instance.iznos if instance.kategorija.tip == "PRIHOD" else -instance.iznos
        cilj = instance.doprinos_cilju
        cilj.trenutno_stanje += new_delta
        cilj.save()

@receiver(pre_delete, sender=Transakcija)
def update_goal_on_delete(sender, instance: Transakcija, **kwargs):
    if instance.doprinos_cilju:
        cilj = instance.doprinos_cilju
        delta = instance.iznos if instance.kategorija.tip == "PRIHOD" else -instance.iznos
        cilj.trenutno_stanje -= delta
        cilj.save()
