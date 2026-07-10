import 'api_client.dart';

String friendlyApiError(Object error) {
  if (error is ApiException) {
    return _humanizeMessage(error.message);
  }

  final text = error.toString().toLowerCase();
  if (_looksLikeNetworkError(text)) {
    return 'Impossible de se connecter. Vérifiez votre réseau et réessayez.';
  }
  if (text.startsWith('apiexception:')) {
    return _humanizeMessage(
      text.replaceFirst('apiexception:', '').trim(),
    );
  }
  return _humanizeMessage(error.toString());
}

bool _looksLikeNetworkError(String text) {
  return text.contains('socketexception') ||
      text.contains('failed host lookup') ||
      text.contains('failed to fetch') ||
      text.contains('connection refused') ||
      text.contains('network is unreachable') ||
      text.contains('clientexception');
}

String _humanizeMessage(String message) {
  final lower = message.toLowerCase();
  if (_looksLikeNetworkError(lower)) {
    return 'Impossible de se connecter. Vérifiez votre réseau et réessayez.';
  }
  if (lower.contains('type') && lower.contains('subtype')) {
    return 'Les données reçues sont incomplètes. Tirez pour actualiser.';
  }
  if (message.length > 120) {
    return '${message.substring(0, 117)}…';
  }
  return message;
}
