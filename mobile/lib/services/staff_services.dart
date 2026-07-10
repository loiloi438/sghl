import '../core/api_client.dart';
import '../models/patient_models.dart';
import '../models/staff_models.dart';

class RendezVousStaffService {
  RendezVousStaffService({ApiClient? apiClient}) : _api = apiClient ?? ApiClient();

  final ApiClient _api;

  Future<RdvStats> fetchStats() async {
    final response = await _api.get('/rendez-vous/stats/');
    return RdvStats.fromJson(_api.decodeMap(response));
  }

  Future<List<JourSemaine>> fetchSemaine({String? anchorDate}) async {
    final path = anchorDate != null
        ? '/rendez-vous/semaine/?date=$anchorDate'
        : '/rendez-vous/semaine/';
    final response = await _api.get(path);
    return _api
        .decodeJsonList(response)
        .map((e) => JourSemaine.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<RendezVousStaff>> fetchList({String? date, String? statut}) async {
    final params = <String>[];
    if (date != null && date.isNotEmpty) params.add('date=$date');
    if (statut != null && statut.isNotEmpty) params.add('statut=$statut');
    final query = params.isEmpty ? '' : '?${params.join('&')}';
    final response = await _api.get('/rendez-vous/$query');
    return _api
        .decodeList(response)
        .map((e) => RendezVousStaff.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<MedecinDispo>> fetchMedecins() async {
    final response = await _api.get('/rendez-vous/medecins/');
    return _api
        .decodeList(response)
        .map((e) => MedecinDispo.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<RendezVousStaff> confirmer({required String rdvId, required int version}) {
    return _action(rdvId, 'confirmer', {'version': version});
  }

  Future<RendezVousStaff> terminer({required String rdvId, required int version}) {
    return _action(rdvId, 'terminer', {'version': version});
  }

  Future<RendezVousStaff> marquerAbsent({required String rdvId, required int version}) {
    return _action(rdvId, 'absent', {'version': version});
  }

  Future<RendezVousStaff> annuler({
    required String rdvId,
    required int version,
    required String motifAnnulation,
  }) {
    return _action(rdvId, 'annuler', {
      'version': version,
      'motif_annulation': motifAnnulation,
    });
  }

  Future<RendezVousStaff> modifier({
    required String rdvId,
    required int version,
    DateTime? dateHeure,
    int? medecinId,
    String? motif,
    String? notes,
    int? dureeMinutes,
    String motifModification = '',
  }) {
    final body = <String, dynamic>{'version': version};
    if (dateHeure != null) {
      body['date_heure'] = dateHeure.toUtc().toIso8601String();
    }
    if (medecinId != null) body['medecin_id'] = medecinId;
    if (motif != null) body['motif'] = motif;
    if (notes != null) body['notes'] = notes;
    if (dureeMinutes != null) body['duree_minutes'] = dureeMinutes;
    if (motifModification.trim().isNotEmpty) {
      body['motif_modification'] = motifModification.trim();
    }
    return _action(rdvId, 'modifier', body);
  }

  Future<RendezVousStaff> _action(
    String rdvId,
    String action,
    Map<String, dynamic> body,
  ) async {
    final response = await _api.post('/rendez-vous/$rdvId/$action/', body);
    return RendezVousStaff.fromJson(_api.decodeMap(response));
  }
}
