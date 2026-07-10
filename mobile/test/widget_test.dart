import 'package:flutter_test/flutter_test.dart';

import 'package:sghl_mobile/models/patient_models.dart';

void main() {
  test('PatientProfil parse JSON', () {
    final profil = PatientProfil.fromJson({
      'id': '550e8400-e29b-41d4-a716-446655440000',
      'numero_dossier': 'P-2026-001',
      'nom': 'MOUANGA',
      'prenom': 'Patient',
      'date_naissance': '1990-05-15',
      'sexe': 'M',
      'telephone': '+242060000000',
      'email': 'patient@sghl.local',
    });

    expect(profil.numeroDossier, 'P-2026-001');
    expect(profil.nom, 'MOUANGA');
  });
}
