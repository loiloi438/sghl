import 'dart:io';

import 'package:flutter/foundation.dart';

import 'api_settings.dart';

class ApiConfig {
  /// Surcharge possible au build :
  /// `flutter build apk --dart-define=API_BASE_URL=http://192.168.1.10:8000/api/v1`
  static const String _buildOverride = String.fromEnvironment('API_BASE_URL');

  static String? _savedOverride;
  static bool _initialized = false;

  static Future<void> init() async {
    if (_initialized) return;
    _savedOverride = await ApiSettings.load();
    _initialized = true;
  }

  static Future<void> setBaseUrl(String url) async {
    final normalized = ApiSettings.normalize(url);
    _savedOverride = normalized;
    await ApiSettings.save(normalized);
  }

  static String get baseUrl {
    if (_buildOverride.isNotEmpty) return _buildOverride;
    if (_savedOverride != null && _savedOverride!.isNotEmpty) {
      return _savedOverride!;
    }

    if (kIsWeb) {
      return 'http://127.0.0.1:8000/api/v1';
    }
    if (!kIsWeb && Platform.isAndroid) {
      // Emulateur Android uniquement ; sur telephone physique, configurer l'URL.
      return 'http://10.0.2.2:8000/api/v1';
    }
    return 'http://127.0.0.1:8000/api/v1';
  }

  /// True si l'app utilise l'URL locale par defaut (emulateur / dev).
  static bool get usesLocalDefault =>
      _buildOverride.isEmpty &&
      (_savedOverride == null || _savedOverride!.isEmpty);

  /// Reecrit les liens web (visio) pour pointer vers le serveur configure.
  static String resolvePublicWebUrl(String url) {
    if (url.isEmpty) return url;
    try {
      final parsed = Uri.parse(url);
      if (parsed.host == 'localhost' || parsed.host == '127.0.0.1') {
        final apiUri = Uri.parse(baseUrl);
        return parsed
            .replace(
              host: apiUri.host,
              port: apiUri.hasPort ? apiUri.port : parsed.port,
            )
            .toString();
      }
    } catch (_) {}
    return url;
  }
}
