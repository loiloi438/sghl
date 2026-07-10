import 'package:flutter_test/flutter_test.dart';

import 'package:sghl_mobile/models/patient_models.dart';

void main() {
  test('PatientProfil converts numeric ids to strings', () {
    final profil = PatientProfil.fromJson({
      'id': 42,
      'numero_dossier': 'P-2026-001',
      'nom': 'MOUANGA',
      'prenom': 'Patient',
      'date_naissance': '1990-05-15',
      'sexe': 'M',
      'telephone': '+242060000000',
      'email': 'patient@sghl.local',
      'adresse': 'Brazzaville',
    });

    expect(profil.id, '42');
    expect(profil.numeroDossier, 'P-2026-001');
  });

  test('FacturePatient parses payment fields', () {
    final facture = FacturePatient.fromJson({
      'id': 'f1-uuid',
      'numero_facture': 'FAC-2026-001',
      'statut': 'validee',
      'montant_total': '15000.00',
      'montant_paye': '5000.00',
      'montant_restant': '10000.00',
      'version': 2,
      'payable_en_ligne': true,
      'validee_le': '2026-07-01T10:00:00Z',
    });

    expect(facture.id, 'f1-uuid');
    expect(facture.montantRestant, '10000.00');
    expect(facture.version, 2);
    expect(facture.payableEnLigne, isTrue);
  });

  test('PatientRegisterResult parses API payload', () {
    final result = PatientRegisterResult.fromJson({
      'username': 'marie.k',
      'detail': 'Compte créé.',
    });
    expect(result.username, 'marie.k');
    expect(result.detail, 'Compte créé.');
  });
}
