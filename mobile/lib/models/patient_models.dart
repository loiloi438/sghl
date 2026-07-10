class UserProfile {
  UserProfile({
    required this.id,
    required this.username,
    required this.email,
    required this.role,
    required this.firstName,
    required this.lastName,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'] as int,
      username: json['username'] as String,
      email: json['email'] as String? ?? '',
      role: json['role'] as String,
      firstName: json['first_name'] as String? ?? '',
      lastName: json['last_name'] as String? ?? '',
    );
  }

  final int id;
  final String username;
  final String email;
  final String role;
  final String firstName;
  final String lastName;

  String get fullName => '$firstName $lastName'.trim();
}

class PatientProfil {
  PatientProfil({
    required this.id,
    required this.numeroDossier,
    required this.nom,
    required this.prenom,
    required this.dateNaissance,
    required this.sexe,
    required this.telephone,
    required this.email,
    required this.adresse,
  });

  factory PatientProfil.fromJson(Map<String, dynamic> json) {
    return PatientProfil(
      id: json['id']?.toString() ?? '',
      numeroDossier: json['numero_dossier'] as String? ?? '',
      nom: json['nom'] as String? ?? '',
      prenom: json['prenom'] as String? ?? '',
      dateNaissance: json['date_naissance'] as String? ?? '',
      sexe: json['sexe'] as String? ?? '',
      telephone: json['telephone'] as String? ?? '',
      email: json['email'] as String? ?? '',
      adresse: json['adresse'] as String? ?? '',
    );
  }

  final String id;
  final String numeroDossier;
  final String nom;
  final String prenom;
  final String dateNaissance;
  final String sexe;
  final String telephone;
  final String email;
  final String adresse;
}

class HospitalisationResume {
  HospitalisationResume({
    required this.id,
    required this.motifAdmission,
    required this.dateAdmission,
    required this.statut,
    required this.litNumero,
    required this.chambreNumero,
    required this.serviceCode,
    required this.batimentCode,
    this.dateSortiePrevue,
  });

  factory HospitalisationResume.fromJson(Map<String, dynamic>? json) {
    if (json == null) {
      throw ArgumentError('Hospitalisation nulle');
    }
    return HospitalisationResume(
      id: json['id']?.toString() ?? '',
      motifAdmission: json['motif_admission'] as String? ?? '',
      dateAdmission: json['date_admission'] as String? ?? '',
      dateSortiePrevue: json['date_sortie_prevue'] as String?,
      statut: json['statut'] as String? ?? '',
      litNumero: json['lit_numero'] as String? ?? '',
      chambreNumero: json['chambre_numero'] as String? ?? '',
      serviceCode: json['service_code'] as String? ?? '',
      batimentCode: json['batiment_code'] as String? ?? '',
    );
  }

  final String id;
  final String motifAdmission;
  final String dateAdmission;
  final String? dateSortiePrevue;
  final String statut;
  final String litNumero;
  final String chambreNumero;
  final String serviceCode;
  final String batimentCode;
}

class ConstanteVitale {
  ConstanteVitale({
    required this.id,
    required this.mesureLe,
    this.temperature,
    this.tensionSystolique,
    this.tensionDiastolique,
    this.frequenceCardiaque,
    this.saturationO2,
  });

  factory ConstanteVitale.fromJson(Map<String, dynamic> json) {
    return ConstanteVitale(
      id: json['id']?.toString() ?? '',
      temperature: (json['temperature'] as num?)?.toDouble(),
      tensionSystolique: (json['tension_systolique'] as num?)?.toInt(),
      tensionDiastolique: (json['tension_diastolique'] as num?)?.toInt(),
      frequenceCardiaque: (json['frequence_cardiaque'] as num?)?.toInt(),
      saturationO2: (json['saturation_o2'] as num?)?.toInt(),
      mesureLe: json['mesure_le'] as String? ?? '',
    );
  }

  final String id;
  final double? temperature;
  final int? tensionSystolique;
  final int? tensionDiastolique;
  final int? frequenceCardiaque;
  final int? saturationO2;
  final String mesureLe;
}

class DoseMedicament {
  DoseMedicament({
    required this.id,
    required this.medicament,
    required this.posologie,
    required this.heurePrevue,
    required this.statut,
    required this.estEnRetard,
  });

  factory DoseMedicament.fromJson(Map<String, dynamic> json) {
    return DoseMedicament(
      id: json['id']?.toString() ?? '',
      medicament: json['medicament'] as String? ?? '',
      posologie: json['posologie'] as String? ?? '',
      heurePrevue: json['heure_prevue'] as String? ?? '',
      statut: json['statut'] as String? ?? '',
      estEnRetard: json['est_en_retard'] as bool? ?? false,
    );
  }

  final String id;
  final String medicament;
  final String posologie;
  final String heurePrevue;
  final String statut;
  final bool estEnRetard;
}

class PlanSoins {
  PlanSoins({
    required this.id,
    required this.titre,
    required this.description,
    required this.statut,
    required this.dateDebut,
  });

  factory PlanSoins.fromJson(Map<String, dynamic> json) {
    return PlanSoins(
      id: json['id']?.toString() ?? '',
      titre: json['titre'] as String? ?? '',
      description: json['description'] as String? ?? '',
      statut: json['statut'] as String? ?? '',
      dateDebut: json['date_debut'] as String? ?? '',
    );
  }

  final String id;
  final String titre;
  final String description;
  final String statut;
  final String dateDebut;
}

class PrescriptionPatient {
  PrescriptionPatient({
    required this.id,
    required this.statut,
    required this.medecinNom,
    this.valideeLe,
    required this.diagnostics,
    required this.medicaments,
  });

  factory PrescriptionPatient.fromJson(Map<String, dynamic> json) {
    return PrescriptionPatient(
      id: json['id']?.toString() ?? '',
      statut: json['statut'] as String? ?? '',
      medecinNom: json['medecin_nom'] as String? ?? '',
      valideeLe: json['validee_le'] as String?,
      diagnostics: (json['diagnostics'] as List<dynamic>? ?? []).cast<String>(),
      medicaments: (json['medicaments'] as List<dynamic>? ?? []).cast<String>(),
    );
  }

  final String id;
  final String statut;
  final String medecinNom;
  final String? valideeLe;
  final List<String> diagnostics;
  final List<String> medicaments;
}

class ResultatLaboPatient {
  ResultatLaboPatient({
    required this.id,
    required this.statut,
    required this.medecinNom,
    this.publieeLe,
    required this.analyses,
  });

  factory ResultatLaboPatient.fromJson(Map<String, dynamic> json) {
    return ResultatLaboPatient(
      id: json['id']?.toString() ?? '',
      statut: json['statut'] as String? ?? '',
      medecinNom: json['medecin_nom'] as String? ?? '',
      publieeLe: json['publiee_le'] as String?,
      analyses: (json['analyses'] as List<dynamic>? ?? []).cast<String>(),
    );
  }

  final String id;
  final String statut;
  final String medecinNom;
  final String? publieeLe;
  final List<String> analyses;
}

class FacturePatient {
  FacturePatient({
    required this.id,
    this.numeroFacture,
    required this.statut,
    required this.montantTotal,
    required this.montantPaye,
    required this.montantRestant,
    required this.version,
    required this.payableEnLigne,
    this.valideeLe,
    this.payeeLe,
  });

  factory FacturePatient.fromJson(Map<String, dynamic> json) {
    return FacturePatient(
      id: json['id']?.toString() ?? '',
      numeroFacture: json['numero_facture'] as String?,
      statut: json['statut'] as String? ?? '',
      montantTotal: json['montant_total']?.toString() ?? '0',
      montantPaye: json['montant_paye']?.toString() ?? '0',
      montantRestant: json['montant_restant']?.toString() ?? '0',
      version: json['version'] as int? ?? 0,
      payableEnLigne: json['payable_en_ligne'] as bool? ?? false,
      valideeLe: json['validee_le'] as String?,
      payeeLe: json['payee_le'] as String?,
    );
  }

  final String id;
  final String? numeroFacture;
  final String statut;
  final String montantTotal;
  final String montantPaye;
  final String montantRestant;
  final int version;
  final bool payableEnLigne;
  final String? valideeLe;
  final String? payeeLe;
}

class PaiementFacture {
  PaiementFacture({
    required this.reference,
    required this.provider,
    required this.amountCents,
    required this.currency,
    required this.status,
    this.clientSecret,
    this.redirectUrl,
    required this.factureSettled,
    this.settlementError,
  });

  factory PaiementFacture.fromJson(Map<String, dynamic> json) {
    return PaiementFacture(
      reference: json['reference'] as String? ?? '',
      provider: json['provider'] as String? ?? '',
      amountCents: json['amount_cents'] as int? ?? 0,
      currency: json['currency'] as String? ?? 'XAF',
      status: json['status'] as String? ?? 'pending',
      clientSecret: json['client_secret'] as String?,
      redirectUrl: json['redirect_url'] as String?,
      factureSettled: json['facture_settled'] as bool? ?? false,
      settlementError: json['settlement_error'] as String?,
    );
  }

  final String reference;
  final String provider;
  final int amountCents;
  final String currency;
  final String status;
  final String? clientSecret;
  final String? redirectUrl;
  final bool factureSettled;
  final String? settlementError;
}

class PaymentStatusResult {
  PaymentStatusResult({
    required this.reference,
    required this.status,
    this.externalId,
    required this.factureSettled,
    this.settlementError,
  });

  factory PaymentStatusResult.fromJson(Map<String, dynamic> json) {
    return PaymentStatusResult(
      reference: json['reference'] as String? ?? '',
      status: json['status'] as String? ?? 'pending',
      externalId: json['external_id'] as String?,
      factureSettled: json['facture_settled'] as bool? ?? false,
      settlementError: json['settlement_error'] as String?,
    );
  }

  final String reference;
  final String status;
  final String? externalId;
  final bool factureSettled;
  final String? settlementError;
}

class PatientRegisterResult {
  PatientRegisterResult({required this.username, required this.detail});

  factory PatientRegisterResult.fromJson(Map<String, dynamic> json) {
    return PatientRegisterResult(
      username: json['username'] as String? ?? '',
      detail: json['detail'] as String? ?? '',
    );
  }

  final String username;
  final String detail;
}

class MedecinDispo {
  MedecinDispo({required this.id, required this.nom});

  factory MedecinDispo.fromJson(Map<String, dynamic> json) {
    return MedecinDispo(id: json['id'] as int, nom: json['nom'] as String);
  }

  final int id;
  final String nom;
}

class RendezVousPatient {
  RendezVousPatient({
    required this.id,
    required this.medecinNom,
    required this.dateHeure,
    required this.dureeMinutes,
    required this.motif,
    required this.statut,
    required this.version,
  });

  factory RendezVousPatient.fromJson(Map<String, dynamic> json) {
    return RendezVousPatient(
      id: json['id']?.toString() ?? '',
      medecinNom: json['medecin_nom'] as String? ?? '',
      dateHeure: json['date_heure'] as String? ?? '',
      dureeMinutes: (json['duree_minutes'] as num?)?.toInt() ?? 30,
      motif: json['motif'] as String? ?? '',
      statut: json['statut'] as String? ?? '',
      version: (json['version'] as num?)?.toInt() ?? 0,
    );
  }

  final String id;
  final String medecinNom;
  final String dateHeure;
  final int dureeMinutes;
  final String motif;
  final String statut;
  final int version;

  bool get peutAnnuler => statut == 'planifie' || statut == 'confirme';

  String get statutLabel {
    switch (statut) {
      case 'planifie':
        return 'Planifié';
      case 'confirme':
        return 'Confirmé';
      case 'annule':
        return 'Annulé';
      case 'termine':
        return 'Terminé';
      case 'absent':
        return 'Absent';
      default:
        return statut;
    }
  }
}

class TableauBord {
  TableauBord({
    required this.profil,
    this.hospitalisationActive,
    required this.prochainesDoses,
    required this.constantesRecentes,
  });

  factory TableauBord.fromJson(Map<String, dynamic> json) {
    return TableauBord(
      profil: PatientProfil.fromJson(json['profil'] as Map<String, dynamic>),
      hospitalisationActive: json['hospitalisation_active'] != null
          ? HospitalisationResume.fromJson(
              json['hospitalisation_active'] as Map<String, dynamic>,
            )
          : null,
      prochainesDoses: (json['prochaines_doses'] as List<dynamic>)
          .map((e) => DoseMedicament.fromJson(e as Map<String, dynamic>))
          .toList(),
      constantesRecentes: (json['constantes_recentes'] as List<dynamic>)
          .map((e) => ConstanteVitale.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  final PatientProfil profil;
  final HospitalisationResume? hospitalisationActive;
  final List<DoseMedicament> prochainesDoses;
  final List<ConstanteVitale> constantesRecentes;
}

class PatientNotification {
  PatientNotification({
    required this.id,
    required this.titre,
    required this.corps,
    required this.categorie,
    required this.lu,
    required this.createdAt,
  });

  factory PatientNotification.fromJson(Map<String, dynamic> json) {
    return PatientNotification(
      id: json['id'] as String,
      titre: json['titre'] as String,
      corps: json['corps'] as String,
      categorie: json['categorie'] as String? ?? '',
      lu: json['lu'] as bool? ?? false,
      createdAt: json['created_at'] as String,
    );
  }

  final String id;
  final String titre;
  final String corps;
  final String categorie;
  final bool lu;
  final String createdAt;
}
