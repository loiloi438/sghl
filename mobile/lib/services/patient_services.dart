import 'package:flutter/foundation.dart';

import '../core/api_client.dart';
import '../core/pdf_download.dart';
import '../models/patient_models.dart';
import 'push_service.dart';

const _staffRdvReadRoles = {'admin', 'medecin', 'infirmier', 'comptable'};
const _staffRdvGestRoles = {'admin', 'medecin', 'infirmier'};

enum LoginStatus { success, mfaRequired, failed }

class AuthService extends ChangeNotifier {
  AuthService({ApiClient? apiClient, PushService? pushService})
      : _api = apiClient ?? ApiClient(),
        _push = pushService;

  final ApiClient _api;
  final PushService? _push;

  UserProfile? _user;
  bool _loading = false;
  String? _error;
  String? _pendingMfaUsername;

  UserProfile? get user => _user;
  bool get loading => _loading;
  String? get error => _error;
  String? get pendingMfaUsername => _pendingMfaUsername;
  bool get isAuthenticated => _user != null;
  bool get isPatient => _user?.role == 'patient';
  bool get isStaffRdv => _staffRdvReadRoles.contains(_user?.role);
  bool get canManageRdv => _staffRdvGestRoles.contains(_user?.role);

  bool _allowedMobileRole(String role) =>
      role == 'patient' || _staffRdvReadRoles.contains(role);

  Future<bool> _finalizeLogin(UserProfile profile) async {
    if (!_allowedMobileRole(profile.role)) {
      await logout();
      _error = 'Ce compte n\'a pas accès à l\'application mobile.';
      return false;
    }
    _user = profile;
    if (profile.role == 'patient') {
      await _push?.registerWithBackend();
    }
    return true;
  }

  Future<bool> tryRestoreSession() async {
    if (!await _api.hasSession()) return false;
    try {
      final response = await _api.get('/auth/me/');
      final profile = UserProfile.fromJson(_api.decodeMap(response));
      if (!_allowedMobileRole(profile.role)) {
        await logout();
        return false;
      }
      _user = profile;
      if (profile.role == 'patient') {
        await _push?.registerWithBackend();
      }
      notifyListeners();
      return true;
    } catch (_) {
      await logout();
      return false;
    }
  }

  Future<LoginStatus> login(String username, String password) async {
    _loading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _api.post(
        '/auth/login/',
        {'username': username, 'password': password},
        auth: false,
      );

      if (response.statusCode == 202) {
        _pendingMfaUsername = username.trim();
        return LoginStatus.mfaRequired;
      }

      final data = _api.decodeMap(response);
      await _api.saveTokens(
        data['access_token'] as String,
        data['refresh_token'] as String,
      );

      final meResponse = await _api.get('/auth/me/');
      final profile = UserProfile.fromJson(_api.decodeMap(meResponse));
      _pendingMfaUsername = null;
      final ok = await _finalizeLogin(profile);
      return ok ? LoginStatus.success : LoginStatus.failed;
    } on ApiException catch (e) {
      if (e.statusCode == 202) {
        _pendingMfaUsername = username.trim();
        return LoginStatus.mfaRequired;
      }
      _error = e.message;
      return LoginStatus.failed;
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  Future<bool> loginMfa(String code) async {
    final username = _pendingMfaUsername;
    if (username == null || username.isEmpty) {
      _error = 'Session MFA expirée. Reconnectez-vous.';
      notifyListeners();
      return false;
    }

    _loading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _api.post(
        '/auth/login/mfa/',
        {'username': username, 'code': code.trim()},
        auth: false,
      );
      final data = _api.decodeMap(response);
      await _api.saveTokens(
        data['access_token'] as String,
        data['refresh_token'] as String,
      );

      final meResponse = await _api.get('/auth/me/');
      final profile = UserProfile.fromJson(_api.decodeMap(meResponse));
      _pendingMfaUsername = null;
      return await _finalizeLogin(profile);
    } on ApiException catch (e) {
      _error = e.message;
      return false;
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  Future<bool> completeValidation(String accessToken, String refreshToken) async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      await _api.saveTokens(accessToken, refreshToken);
      final meResponse = await _api.get('/auth/me/');
      final profile = UserProfile.fromJson(_api.decodeMap(meResponse));
      return await _finalizeLogin(profile);
    } on ApiException catch (e) {
      _error = e.message;
      return false;
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  void clearMfaPending() {
    _pendingMfaUsername = null;
    _error = null;
    notifyListeners();
  }

  Future<void> logout() async {
    await _push?.unregisterFromBackend();
    _user = null;
    _pendingMfaUsername = null;
    await _api.clearTokens();
    notifyListeners();
  }
}

class PatientService {
  PatientService({ApiClient? apiClient}) : _api = apiClient ?? ApiClient();

  final ApiClient _api;

  Future<TableauBord> fetchDashboard() async {
    final response = await _api.get('/patient/tableau-de-bord/');
    return TableauBord.fromJson(_api.decodeMap(response));
  }

  Future<List<HospitalisationResume>> fetchHospitalisations() async {
    final response = await _api.get('/patient/hospitalisations/');
    return _api
        .decodeList(response)
        .map((e) => HospitalisationResume.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<PatientMessage>> fetchMessages() async {
    final response = await _api.get('/patient/messages/');
    return _api
        .decodeList(response)
        .map((e) => PatientMessage.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<PatientMessage> sendMessage({
    required String sujet,
    required String corps,
  }) async {
    final response = await _api.post('/patient/messages/', {
      'sujet': sujet.trim(),
      'corps': corps.trim(),
    });
    return PatientMessage.fromJson(_api.decodeMap(response));
  }

  Future<List<ConstanteVitale>> fetchConstantes() async {
    final response = await _api.get('/patient/constantes-vitales/');
    return _api
        .decodeList(response)
        .map((e) => ConstanteVitale.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<PlanSoins>> fetchPlansSoins() async {
    final response = await _api.get('/patient/plans-soins/');
    return _api
        .decodeList(response)
        .map((e) => PlanSoins.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<DoseMedicament>> fetchDoses() async {
    final response = await _api.get('/patient/doses/');
    return _api
        .decodeList(response)
        .map((e) => DoseMedicament.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<PrescriptionPatient>> fetchPrescriptions() async {
    final response = await _api.get('/patient/prescriptions/');
    return _api
        .decodeList(response)
        .map((e) => PrescriptionPatient.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<ResultatLaboPatient>> fetchResultatsLaboratoire() async {
    final response = await _api.get('/patient/resultats-laboratoire/');
    return _api
        .decodeList(response)
        .map((e) => ResultatLaboPatient.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<FacturePatient>> fetchFactures() async {
    final response = await _api.get('/patient/factures/');
    return _api
        .decodeList(response)
        .map((e) => FacturePatient.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<PaiementFacture> initierPaiementFacture({
    required String factureId,
    required String provider,
    required int version,
  }) async {
    final response = await _api.post(
      '/patient/factures/$factureId/initier-paiement/',
      {'provider': provider, 'version': version},
    );
    return PaiementFacture.fromJson(_api.decodeMap(response));
  }

  Future<PaymentStatusResult> pollPaymentStatus(String reference) async {
    final response = await _api.get('/payments/$reference/status/');
    return PaymentStatusResult.fromJson(_api.decodeMap(response));
  }

  Future<void> downloadPrescriptionPdf(String prescriptionId) async {
    final bytes = await _api.downloadBytes('/prescriptions/$prescriptionId/pdf/');
    await PdfDownloadHelper.saveAndOpen(bytes, 'ordonnance-$prescriptionId.pdf');
  }

  Future<void> downloadLaboPdf(String commandeId) async {
    final bytes = await _api.downloadBytes('/commandes-analyses/$commandeId/pdf/');
    await PdfDownloadHelper.saveAndOpen(bytes, 'labo-$commandeId.pdf');
  }

  Future<void> downloadFacturePdf(String factureId, {String? numeroFacture}) async {
    final bytes = await _api.downloadBytes('/facturation/factures/$factureId/pdf/');
    final name = numeroFacture != null && numeroFacture.isNotEmpty
        ? '$numeroFacture.pdf'
        : 'facture-$factureId.pdf';
    await PdfDownloadHelper.saveAndOpen(bytes, name);
  }

  Future<void> downloadRecuPdf(String factureId, {String? numeroFacture}) async {
    final bytes = await _api.downloadBytes('/facturation/factures/$factureId/recu/');
    final name = numeroFacture != null && numeroFacture.isNotEmpty
        ? 'recu-$numeroFacture.pdf'
        : 'recu-$factureId.pdf';
    await PdfDownloadHelper.saveAndOpen(bytes, name);
  }

  Future<List<RendezVousPatient>> fetchRendezVous() async {
    final response = await _api.get('/patient/rendez-vous/');
    return _api
        .decodeList(response)
        .map((e) => RendezVousPatient.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<MedecinDispo>> fetchMedecins() async {
    final response = await _api.get('/patient/rendez-vous/medecins/');
    return _api
        .decodeList(response)
        .map((e) => MedecinDispo.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<PatientProfil> fetchProfil() async {
    final response = await _api.get('/patient/profil/');
    return PatientProfil.fromJson(_api.decodeMap(response));
  }

  Future<RendezVousPatient> creerRendezVous({
    required int medecinId,
    required DateTime dateHeure,
    required String motif,
    int dureeMinutes = 30,
    required String email,
    required String emailConfirm,
    required String telephone,
    String adresse = '',
    String typeConsultation = 'presentiel',
  }) async {
    final response = await _api.post('/patient/rendez-vous/', {
      'medecin_id': medecinId,
      'date_heure': dateHeure.toUtc().toIso8601String(),
      'motif': motif,
      'duree_minutes': dureeMinutes,
      'email': email.trim(),
      'email_confirm': emailConfirm.trim(),
      'telephone': telephone.trim(),
      'adresse': adresse.trim(),
      'type_consultation': typeConsultation,
    });
    return RendezVousPatient.fromJson(_api.decodeMap(response));
  }

  Future<RendezVousPatient> annulerRendezVous({
    required String rdvId,
    required int version,
    String motifAnnulation = '',
  }) async {
    final response = await _api.post('/patient/rendez-vous/$rdvId/annuler/', {
      'version': version,
      'motif_annulation': motifAnnulation,
    });
    return RendezVousPatient.fromJson(_api.decodeMap(response));
  }

  Future<PatientRegisterResult> registerPatient({
    required String nom,
    required String prenom,
    required String dateNaissance,
    required String sexe,
    required String email,
    required String telephone,
    required String password,
    required String passwordConfirm,
    required bool consentementRgpd,
  }) async {
    final response = await _api.post('/auth/register/patient/', {
      'nom': nom.trim(),
      'prenom': prenom.trim(),
      'date_naissance': dateNaissance,
      'sexe': sexe,
      'email': email.trim(),
      'telephone': telephone.trim(),
      'password': password,
      'password_confirm': passwordConfirm,
      'consentement_rgpd': consentementRgpd,
    }, auth: false);
    return PatientRegisterResult.fromJson(_api.decodeMap(response));
  }

  Future<ValidateAccountResult> validateAccount({
    required String username,
    required String code,
  }) async {
    final response = await _api.post('/auth/validate/', {
      'username': username.trim(),
      'code': code.trim(),
    }, auth: false);
    final data = _api.decodeMap(response);
    return ValidateAccountResult.fromJson(data);
  }

  Future<String> resendValidationCode(String username) async {
    final response = await _api.post('/auth/validate/resend/', {
      'username': username.trim(),
    }, auth: false);
    final data = _api.decodeMap(response);
    return data['detail'] as String? ?? 'Code renvoyé.';
  }
}
