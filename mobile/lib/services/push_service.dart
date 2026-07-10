import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:uuid/uuid.dart';

import '../core/api_client.dart';

/// Enregistre un jeton appareil (mode dev sans Firebase ou jeton FCM futur).
class PushService {
  PushService({required ApiClient apiClient}) : _api = apiClient;

  final ApiClient _api;
  static const _tokenKey = 'sghl_push_device_token';
  final _uuid = const Uuid();

  Future<String> getOrCreateDeviceToken() async {
    final prefs = await SharedPreferences.getInstance();
    var token = prefs.getString(_tokenKey);
    if (token == null || token.isEmpty) {
      token = 'sghl-dev:${_uuid.v4()}';
      await prefs.setString(_tokenKey, token);
    }
    return token;
  }

  String _plateforme() {
    if (kIsWeb) return 'web';
    if (Platform.isAndroid) return 'android';
    if (Platform.isIOS) return 'ios';
    return 'inconnu';
  }

  Future<void> registerWithBackend() async {
    final token = await getOrCreateDeviceToken();
    await _api.post('/patient/push/appareils/', {
      'token': token,
      'plateforme': _plateforme(),
    });
  }

  Future<void> unregisterFromBackend() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString(_tokenKey);
    if (token == null) return;
    try {
      await _api.post('/patient/push/appareils/desactiver/', {
        'token': token,
        'plateforme': _plateforme(),
      });
    } catch (_) {}
  }
}
