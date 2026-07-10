import 'dart:io';

import 'package:flutter/foundation.dart';

class ApiConfig {
  /// Surcharge possible au lancement :
  /// `flutter run --dart-define=API_BASE_URL=http://192.168.1.10:8000/api/v1`
  static const String _override = String.fromEnvironment('API_BASE_URL');

  static String get baseUrl {
    if (_override.isNotEmpty) return _override;

    if (kIsWeb) {
      return 'http://127.0.0.1:8000/api/v1';
    }
    if (!kIsWeb && Platform.isAndroid) {
      // Émulateur Android → machine hôte Windows
      return 'http://10.0.2.2:8000/api/v1';
    }
    // Windows desktop, iOS simulateur, etc.
    return 'http://127.0.0.1:8000/api/v1';
  }

  /// Réécrit les liens web (visio) pour l'émulateur Android.
  static String resolvePublicWebUrl(String url) {
    if (url.isEmpty) return url;
    if (!kIsWeb && Platform.isAndroid) {
      return url
          .replaceFirst('http://localhost:', 'http://10.0.2.2:')
          .replaceFirst('http://127.0.0.1:', 'http://10.0.2.2:');
    }
    return url;
  }
}
