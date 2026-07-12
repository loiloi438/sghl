import 'dart:convert';

import 'api_client.dart';
import 'api_session.dart';

const kStaffOnlyMessage =
    'Cette fonctionnalité est réservée au personnel médical 💙';

String friendlyNetworkError({bool serverWaking = false}) {
  if (serverWaking) {
    return 'Le service SGHL se réveille… Réessayez dans quelques secondes 💙';
  }
  return 'Connexion momentanément indisponible. Vérifiez votre réseau et réessayez dans quelques instants.';
}

String friendlyLoginError(int statusCode, String body) {
  if (statusCode == 401) {
    return 'Identifiants incorrects. Vérifiez votre identifiant et mot de passe.';
  }
  if (statusCode == 403) {
    return _humanizeMessage(
      friendlyHttpError(statusCode, body, isPatient: true),
      isPatient: true,
    );
  }
  return friendlyHttpError(statusCode, body, isPatient: true);
}

String friendlyHttpError(int statusCode, String body, {bool? isPatient}) {
  final patient = isPatient ?? ApiSession.isPatient;

  if (statusCode == 401) {
    return patient
        ? 'Votre session a expiré. Reconnectez-vous pour continuer 💙'
        : 'Session expirée. Reconnectez-vous.';
  }
  if (statusCode == 403) {
    return patient ? kStaffOnlyMessage : 'Accès refusé pour votre rôle.';
  }
  if (statusCode == 404) {
    return 'Service momentanément indisponible. Réessayez plus tard.';
  }
  if (statusCode >= 500) {
    return 'Nos services sont temporairement indisponibles. Réessayez dans un instant.';
  }

  try {
    final data = jsonDecode(body);
    if (data is Map<String, dynamic>) {
      final raw = (data['detail'] ?? data['message'] ?? data['error'] ?? '').toString();
      if (raw.isNotEmpty) {
        return _humanizeMessage(raw, isPatient: patient);
      }
    }
  } catch (_) {}

  return 'Une erreur est survenue. Veuillez réessayer.';
}

String friendlyApiError(Object error, {bool? isPatient}) {
  if (error is ApiException) {
    return _humanizeMessage(error.message, isPatient: isPatient);
  }

  final text = error.toString().toLowerCase();
  if (isNetworkErrorText(text)) {
    return friendlyNetworkError();
  }
  if (text.startsWith('apiexception:')) {
    return _humanizeMessage(
      text.replaceFirst('apiexception:', '').trim(),
      isPatient: isPatient,
    );
  }
  return _humanizeMessage(error.toString(), isPatient: isPatient);
}

bool isNetworkError(Object error) {
  return isNetworkErrorText(error.runtimeType.toString().toLowerCase()) ||
      isNetworkErrorText(error.toString().toLowerCase());
}

bool isNetworkErrorText(String text) {
  return text.contains('socketexception') ||
      text.contains('failed host lookup') ||
      text.contains('failed to fetch') ||
      text.contains('connection refused') ||
      text.contains('network is unreachable') ||
      text.contains('clientexception') ||
      text.contains('delai depasse') ||
      text.contains('timeoutexception') ||
      text.contains('serveur sghl') ||
      text.contains('verifiez l\'url') ||
      text.contains('backend tourne') ||
      text.contains('runserver');
}

String _humanizeMessage(String message, {bool? isPatient}) {
  final patient = isPatient ?? ApiSession.isPatient;
  final lower = message.toLowerCase();

  if (isNetworkErrorText(lower)) {
    return friendlyNetworkError();
  }
  if (lower.contains('unauthorized') ||
      lower.contains('non autoris') ||
      lower.contains('not authenticated')) {
    return patient
        ? 'Votre session a expiré. Reconnectez-vous pour continuer 💙'
        : 'Session expirée. Reconnectez-vous.';
  }
  if (lower.contains('forbidden') ||
      lower.contains('accès refusé') ||
      lower.contains('acces refuse') ||
      lower.contains('permission') ||
      lower.contains('réservé') ||
      lower.contains('reserve')) {
    return patient ? kStaffOnlyMessage : 'Accès refusé pour votre rôle.';
  }
  if (lower.contains('invalid') ||
      lower.contains('incorrect') ||
      lower.contains('credentials') ||
      lower.contains('identifiants')) {
    return 'Identifiants incorrects. Vérifiez votre identifiant et mot de passe.';
  }
  if (lower.contains('type') && lower.contains('subtype')) {
    return 'Les données reçues sont incomplètes. Tirez pour actualiser.';
  }
  if (lower.contains('erreur serveur') || lower.contains('statuscode')) {
    return 'Une erreur est survenue. Veuillez réessayer.';
  }
  if (message.length > 120) {
    return '${message.substring(0, 117)}…';
  }
  return message;
}
