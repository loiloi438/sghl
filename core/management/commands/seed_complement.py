from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Role, User
from assurance.models import OrganismeAssurance
from core.models import ConfigurationEtablissement
from inventaire.models import ArticleStock
from patients.models import Patient
from rendezvous.models import RendezVous, TypeConsultation
from urgences.models import PassageUrgence


class Command(BaseCommand):
    help = 'Données de démo pour assurance, inventaire, urgences, paramètres, téléconsultation.'

    def handle(self, *args, **options):
        cfg = ConfigurationEtablissement.get_solo()
        cfg.organization_name = 'SGHL — Centre Hospitalier de Libreville'
        cfg.address = 'Boulevard Triomphal, Libreville, Gabon'
        cfg.phone = '+241 01 00 00 00'
        cfg.email = 'support@sghl.local'
        cfg.finess_number = '750000001'
        cfg.save()
        self.stdout.write(self.style.SUCCESS('Configuration établissement initialisée.'))

        for code, nom, taux in [
            ('CIMR', 'CIMR', 90),
            ('CNSS', 'CNSS', 80),
            ('MUT', 'MUTUELLE SANTÉ', 60),
        ]:
            OrganismeAssurance.objects.get_or_create(
                code=code,
                defaults={'nom': nom, 'taux_couverture': taux, 'actif': True},
            )

        articles = [
            ('GANT-L', 'Gants latex (L)', 'consumable', 500, 100, 'paire', '12.50'),
            ('SER-5ML', 'Seringues 5 ml', 'consumable', 200, 50, 'unité', '0.80'),
            ('MON-PULS', 'Moniteur multiparamétrique', 'equipment', 8, 2, 'unité', '4500.00'),
        ]
        for code, nom, cat, qty, seuil, unite, val in articles:
            ArticleStock.objects.get_or_create(
                code=code,
                defaults={
                    'nom': nom,
                    'categorie': cat,
                    'quantite': qty,
                    'seuil_alerte': seuil,
                    'unite': unite,
                    'valeur_unitaire': Decimal(val),
                },
            )

        patient = Patient.objects.first()
        passages = [
            ('Ahmed ZAKI', 45, 'M', 'Douleur thoracique', 'red'),
            ('Fatima BRAHIM', 32, 'F', 'Chute, douleur à la jambe', 'orange'),
        ]
        for nom, age, sexe, motif, triage in passages:
            PassageUrgence.objects.get_or_create(
                nom_libre=nom,
                motif=motif,
                defaults={'age': age, 'sexe': sexe, 'niveau_triage': triage},
            )

        medecin = User.objects.filter(role=Role.MEDECIN).first()
        if patient and medecin:
            future = timezone.now() + timedelta(days=2)
            RendezVous.objects.get_or_create(
                patient=patient,
                medecin=medecin,
                date_heure=future,
                defaults={
                    'motif': 'Suivi post-opératoire à distance',
                    'type_consultation': TypeConsultation.TELECONSULTATION,
                    'lien_visio': 'http://127.0.0.1:5173/visio/demo-token',
                    'duree_minutes': 30,
                },
            )

        self.stdout.write(self.style.SUCCESS('Modules complémentaires initialisés.'))
