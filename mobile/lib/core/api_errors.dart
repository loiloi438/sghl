import 'dart:convert';

import 'api_client.dart';

String friendlyNetworkError() {
  return 'Connexion momentanément indisponible. Vérifiez votre réseau et réessayez dans quelques instants.';
}

String friendlyHttpError(int statusCode, String body) {
  if (statusCode == 401 || statusCode == 403) {
    return 'Identifiants incorrects ou session expirée.';
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
      if (raw.isNotEmpty) return _humanizeMessage(raw);
    }
  } catch (_) {}

  return 'Une erreur est survenue. Veuillez réessayer.';
}

String friendlyApiError(Object error) {
  if (error is ApiException) {
    return _humanizeMessage(error.message);
  }

  final text = error.toString().toLowerCase();
  if (isNetworkErrorText(text)) {
    return friendlyNetworkError();
  }
  if (text.startsWith('apiexception:')) {
    return _humanizeMessage(
      text.replaceFirst('apiexception:', '').trim(),
    );
  }
  return _humanizeMessage(error.toString());
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

String _humanizeMessage(String message) {
  final lower = message.toLowerCase();
  if (isNetworkErrorText(lower)) {
    return friendlyNetworkError();
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
