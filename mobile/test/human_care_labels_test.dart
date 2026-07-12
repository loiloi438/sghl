import 'package:flutter_test/flutter_test.dart';

import 'package:sghl_mobile/models/patient_models.dart';

void main() {
  test('HospitalisationResume parses active stay', () {
    final item = HospitalisationResume.fromJson({
      'id': 'h1',
      'statut': 'active',
      'motif_admission': 'Suivi post-opératoire',
      'date_admission': '2026-07-01T08:00:00Z',
      'service_nom': 'Chirurgie',
      'service_code': 'CHIR',
      'batiment_code': 'A',
      'medecin_nom': 'Dr. Martin',
      'chambre_numero': '12',
      'lit_numero': '2',
    });

    expect(item.statut, 'active');
    expect(item.motifAdmission, 'Suivi post-opératoire');
    expect(item.medecinNom, 'Dr. Martin');
  });

  test('ResultatLaboPatient parses published lab bundle', () {
    final item = ResultatLaboPatient.fromJson({
      'id': 'r1',
      'statut': 'publie',
      'medecin_nom': 'Dr. Martin',
      'publiee_le': '2026-07-05T09:30:00Z',
      'analyses': ['Glycémie', 'HbA1c'],
    });

    expect(item.statut, 'publie');
    expect(item.medecinNom, 'Dr. Martin');
    expect(item.analyses, ['Glycémie', 'HbA1c']);
  });
}
