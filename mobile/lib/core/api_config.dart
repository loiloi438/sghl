import 'package:flutter/foundation.dart';

import 'api_settings.dart';

class ApiConfig {
  static const String productionApiUrl = 'https://sghl-api.onrender.com/api/v1';

  /// Surcharge possible au build :
  /// `flutter build web --dart-define=API_BASE_URL=https://sghl-api.onrender.com/api/v1`
  static const String _buildOverride = String.fromEnvironment('API_BASE_URL');

  static String? _savedOverride;
  static bool _initialized = false;

  static Future<void> init() async {
    if (_initialized) return;
    _savedOverride = await ApiSettings.load();
    if (kIsWeb && _hostedProductionHost &&
        _savedOverride != null &&
        _isLocalUrl(_savedOverride!)) {
      _savedOverride = null;
      await ApiSettings.clear();
    }
    _initialized = true;
  }

  static Future<void> setBaseUrl(String url) async {
    final normalized = ApiSettings.normalize(url);
    _savedOverride = normalized;
    await ApiSettings.save(normalized);
  }

  static bool get isProductionDeployment {
    if (_buildOverride.isNotEmpty && !_isLocalUrl(_buildOverride)) {
      return true;
    }
    return kIsWeb && _hostedProductionHost;
  }

  static bool get showServerSettings => !isProductionDeployment;

  static String get baseUrl {
    if (_buildOverride.isNotEmpty) return _buildOverride;
    if (_savedOverride != null && _savedOverride!.isNotEmpty) {
      if (kIsWeb && _hostedProductionHost && _isLocalUrl(_savedOverride!)) {
        return productionApiUrl;
      }
      return _savedOverride!;
    }

    if (kIsWeb) {
      return _hostedProductionHost ? productionApiUrl : 'http://127.0.0.1:8000/api/v1';
    }
    if (defaultTargetPlatform == TargetPlatform.android) {
      return 'http://10.0.2.2:8000/api/v1';
    }
    return 'http://127.0.0.1:8000/api/v1';
  }

  static bool get usesLocalDefault =>
      !isProductionDeployment &&
      _buildOverride.isEmpty &&
      (_savedOverride == null || _savedOverride!.isEmpty);

  static bool get _hostedProductionHost {
    if (!kIsWeb) return false;
    final host = Uri.base.host.toLowerCase();
    if (host.isEmpty) return false;
    return host.endsWith('onrender.com') ||
        (!host.contains('localhost') && !host.startsWith('127.'));
  }

  static bool _isLocalUrl(String url) {
    final lower = url.toLowerCase();
    return lower.contains('127.0.0.1') ||
        lower.contains('localhost') ||
        lower.contains('10.0.2.2') ||
        lower.contains('192.168.');
  }

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
