from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Role, User
from logistics.models import Service
from rh.models import Certification, Formation, StatutFormation, StatutInscription
from rh.services import (
    attribuer_certification,
    creer_garde,
    inscrire_personnel,
)


class Command(BaseCommand):
    help = 'Crée des données RH de démonstration (formations, certifications, gardes).'

    def handle(self, *args, **options):
        staff = list(
            User.objects.filter(
                role__in={Role.MEDECIN, Role.INFIRMIER, Role.BIOLOGISTE, Role.PHARMACIEN},
            ).order_by('id')[:6],
        )
        if not staff:
            self.stdout.write(self.style.WARNING('Aucun personnel staff — lancez seed_demo d’abord.'))
            return

        service = Service.objects.first()

        rcp, _ = Certification.objects.get_or_create(
            nom='RCP (Réanimation Cardio-Pulmonaire)',
            defaults={
                'type_certification': 'Secourisme',
                'duree_validite_mois': 24,
            },
        )
        iso, _ = Certification.objects.get_or_create(
            nom='ISO 9001 Quality',
            defaults={
                'type_certification': 'Management',
                'duree_validite_mois': 36,
            },
        )

        today = date.today()
        for i, user in enumerate(staff[:4]):
            attribuer_certification(
                certification=rcp,
                personnel=user,
                date_obtention=today - timedelta(days=400),
                date_expiration=today + timedelta(days=30 if i == 0 else 200),
                numero_certificat=f'RCP-{user.id:04d}',
            )
        for user in staff[:2]:
            attribuer_certification(
                certification=iso,
                personnel=user,
                date_obtention=today - timedelta(days=100),
                date_expiration=today + timedelta(days=500),
                numero_certificat=f'ISO-{user.id:04d}',
            )

        formations_data = [
            ('RCP Adulte & Pédiatrie', 'Dr Karim', today + timedelta(days=5), today + timedelta(days=7), StatutFormation.PROGRAMMEE),
            ('Hygiène et Biosécurité', 'Inspectrice ICAC', today - timedelta(days=1), today + timedelta(days=1), StatutFormation.EN_COURS),
            ('Management d\'équipe', 'Coach RH', today - timedelta(days=20), today - timedelta(days=18), StatutFormation.TERMINEE),
        ]
        for titre, formateur, debut, fin, statut in formations_data:
            formation, created = Formation.objects.get_or_create(
                titre=titre,
                date_debut=debut,
                defaults={
                    'formateur': formateur,
                    'date_fin': fin,
                    'capacite_max': 25,
                    'statut': statut,
                },
            )
            if created:
                for user in staff[:3]:
                    try:
                        inscr = inscrire_personnel(formation=formation, personnel=user)
                        if statut == StatutFormation.TERMINEE:
                            inscr.statut = StatutInscription.VALIDE
                            inscr.save(update_fields=['statut'])
                    except Exception:
                        pass

        now = timezone.now()
        for i, user in enumerate(staff[:3]):
            debut = now.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=i)
            fin = debut + timedelta(hours=12)
            try:
                creer_garde(
                    personnel=user,
                    type_garde='jour' if i % 2 == 0 else 'nuit',
                    date_debut=debut,
                    date_fin=fin,
                    service=service,
                    notes='Garde de démonstration',
                )
            except Exception:
                pass

        self.stdout.write(self.style.SUCCESS('Données RH de démonstration créées.'))
