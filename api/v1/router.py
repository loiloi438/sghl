from ninja import NinjaAPI

from api.v1.auth import router as auth_router
from api.v1.audit_logs import router as audit_logs_router
from api.v1.dashboard import router as dashboard_router
from api.v1.health import router as health_router
from api.v1.hospitalisation import router as hospitalisation_router
from api.v1.logistics import router as logistics_router
from api.v1.personnel import router as personnel_router
from api.v1.notifications import router as notifications_router
from api.v1.patient_portal import router as patient_portal_router
from api.v1.patients import router as patients_router
from api.v1.services import router as services_router
from api.v1.statistiques import router as statistiques_router
from api.v1.documents import router as documents_router
from api.v1.facturation import router as facturation_router
from api.v1.laboratoire import router as laboratoire_router
from api.v1.pharmacie import router as pharmacie_router
from api.v1.prescriptions import router as prescriptions_router
from api.v1.rendezvous import router as rendezvous_router
from api.v1.soins import router as soins_router
from api.v1.payments import router as payments_router
from api.v1.rh import router as rh_router
from api.v1.parametres import router as parametres_router
from api.v1.assurance import router as assurance_router
from api.v1.inventaire import router as inventaire_router
from api.v1.urgences import router as urgences_router
from api.v1.teleconsultation import router as teleconsultation_router
from api.v1.messagerie import router as messagerie_router

from django.conf import settings

if settings.DEBUG:
    from api.v1.e2e_helpers import router as e2e_helpers_router

api = NinjaAPI(
    title='SGHL API',
    version='1.0.0',
    description='Système de Gestion Hospitalière et de Laboratoire',
)

api.add_router('', health_router)
api.add_router('', auth_router)
api.add_router('', dashboard_router)
api.add_router('', audit_logs_router)
api.add_router('', patient_portal_router)
api.add_router('', hospitalisation_router)
api.add_router('', soins_router)
api.add_router('', prescriptions_router)
api.add_router('', laboratoire_router)
api.add_router('', pharmacie_router)
api.add_router('', rendezvous_router)
api.add_router('', notifications_router)
api.add_router('', services_router)
api.add_router('', personnel_router)
api.add_router('', statistiques_router)
api.add_router('', documents_router)
api.add_router('', facturation_router)
api.add_router('', logistics_router)
api.add_router('', patients_router)
api.add_router('', payments_router)
api.add_router('', rh_router)
api.add_router('', parametres_router)
api.add_router('', assurance_router)
api.add_router('', inventaire_router)
api.add_router('', urgences_router)
api.add_router('', teleconsultation_router)
api.add_router('', messagerie_router)
if settings.DEBUG:
    api.add_router('', e2e_helpers_router)
