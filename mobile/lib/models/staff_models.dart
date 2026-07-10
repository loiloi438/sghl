class RdvStats {
  RdvStats({required this.rdvAujourdhui, required this.rdvPlanifies});

  factory RdvStats.fromJson(Map<String, dynamic> json) {
    return RdvStats(
      rdvAujourdhui: json['rdv_aujourdhui'] as int,
      rdvPlanifies: json['rdv_planifies'] as int,
    );
  }

  final int rdvAujourdhui;
  final int rdvPlanifies;
}

class JourSemaine {
  JourSemaine({required this.date, required this.count});

  factory JourSemaine.fromJson(Map<String, dynamic> json) {
    return JourSemaine(
      date: json['date'] as String,
      count: json['count'] as int,
    );
  }

  final String date;
  final int count;
}

class RendezVousStaff {
  RendezVousStaff({
    required this.id,
    required this.patientId,
    required this.numeroDossier,
    required this.patientNom,
    required this.medecinId,
    required this.medecinNom,
    required this.dateHeure,
    required this.dureeMinutes,
    required this.motif,
    required this.statut,
    required this.notes,
    required this.version,
  });

  factory RendezVousStaff.fromJson(Map<String, dynamic> json) {
    return RendezVousStaff(
      id: json['id'] as String,
      patientId: json['patient_id'] as String,
      numeroDossier: json['numero_dossier'] as String,
      patientNom: json['patient_nom'] as String,
      medecinId: json['medecin_id'] as int,
      medecinNom: json['medecin_nom'] as String,
      dateHeure: json['date_heure'] as String,
      dureeMinutes: json['duree_minutes'] as int,
      motif: json['motif'] as String,
      statut: json['statut'] as String,
      notes: json['notes'] as String? ?? '',
      version: json['version'] as int,
    );
  }

  final String id;
  final String patientId;
  final String numeroDossier;
  final String patientNom;
  final int medecinId;
  final String medecinNom;
  final String dateHeure;
  final int dureeMinutes;
  final String motif;
  final String statut;
  final String notes;
  final int version;

  bool get peutGerer => statut == 'planifie' || statut == 'confirme';

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
