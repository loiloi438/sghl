from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Role, User
from patients.models import Patient
from rendezvous.models import RendezVous, StatutRendezVous
from rendezvous.services import confirmer_rendez_vous, creer_rendez_vous


class Command(BaseCommand):
    help = 'Crée des rendez-vous de démonstration.'

    def handle(self, *args, **options):
        patient = Patient.objects.filter(numero_dossier='P-2026-001').first()
        medecin = User.objects.filter(username='medecin', role=Role.MEDECIN).first()
        infirmier = User.objects.filter(role=Role.INFIRMIER).first()

        if not patient or not medecin:
            self.stdout.write(self.style.WARNING('Patient P-2026-001 ou médecin absent — lancez seed_demo.'))
            return

        auteur = infirmier or medecin
        now = timezone.now()

        demos = [
            (now + timedelta(hours=2), 'Consultation de suivi', StatutRendezVous.CONFIRME),
            (now + timedelta(days=1, hours=10), 'Bilan post-hospitalisation', StatutRendezVous.PLANIFIE),
            (now + timedelta(days=3, hours=9), 'Contrôle tension', StatutRendezVous.PLANIFIE),
        ]

        created = 0
        for date_heure, motif, statut_cible in demos:
            exists = RendezVous.objects.filter(
                patient=patient,
                medecin=medecin,
                motif=motif,
            ).exists()
            if exists:
                continue
            rdv = creer_rendez_vous(
                patient=patient,
                medecin=medecin,
                date_heure=date_heure,
                motif=motif,
                auteur=auteur,
            )
            if statut_cible == StatutRendezVous.CONFIRME:
                confirmer_rendez_vous(rdv=rdv, auteur=auteur, version=rdv.version)
            created += 1

        self.stdout.write(self.style.SUCCESS(f'{created} rendez-vous démo créé(s).'))
