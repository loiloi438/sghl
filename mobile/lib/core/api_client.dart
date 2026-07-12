import 'dart:convert';
import 'dart:async';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

import 'api_config.dart';
import 'api_errors.dart';
import 'api_session.dart';

class ApiException implements Exception {
  ApiException(this.message, {this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() => message;
}

class ApiClient {
  ApiClient({FlutterSecureStorage? storage})
      : _storage = storage ?? const FlutterSecureStorage();

  final FlutterSecureStorage _storage;
  static const _accessKey = 'sghl_access_token';
  static const _refreshKey = 'sghl_refresh_token';
  static const _requestTimeout = Duration(seconds: 60);
  static const _networkRetryDelays = [
    Duration(seconds: 2),
    Duration(seconds: 4),
    Duration(seconds: 6),
  ];

  Future<Map<String, String>> _headers({bool auth = true, bool binary = false}) async {
    final headers = <String, String>{
      'Accept': 'application/json',
    };
    if (!binary) {
      headers['Content-Type'] = 'application/json';
    }
    if (auth) {
      final token = await _storage.read(key: _accessKey);
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }
    }
    return headers;
  }

  Future<http.Response> get(String path, {bool auth = true}) {
    return _request('GET', path, auth: auth);
  }

  Future<http.Response> post(String path, Map<String, dynamic> body, {bool auth = true}) {
    return _request('POST', path, auth: auth, body: body);
  }

  Future<http.Response> patch(
    String path,
    Map<String, dynamic> body, {
    bool auth = true,
  }) {
    return _request('PATCH', path, auth: auth, body: body);
  }

  /// Réveille l'API Render (cold start) avant une connexion.
  Future<void> warmUp({int attempts = 3}) async {
    Object? lastError;
    for (var i = 0; i < attempts; i++) {
      try {
        final response = await http
            .get(
              Uri.parse('${ApiConfig.baseUrl}/sante/'),
              headers: const {'Accept': 'application/json'},
            )
            .timeout(_requestTimeout);
        if (response.statusCode < 500) return;
      } catch (e) {
        lastError = e;
      }
      if (i < attempts - 1) {
        await Future<void>.delayed(_networkRetryDelays[i]);
      }
    }
    if (lastError != null && isNetworkError(lastError)) {
      throw ApiException(friendlyNetworkError(serverWaking: true));
    }
  }

  Future<List<int>> downloadBytes(String path, {bool auth = true}) async {
    final response = await _request('GET', path, auth: auth, binary: true);
    if (response.statusCode >= 400) {
      await _notifyHttpError(response.statusCode);
      throw ApiException(
        friendlyHttpError(response.statusCode, response.body),
        statusCode: response.statusCode,
      );
    }
    return response.bodyBytes;
  }

  Future<void> saveTokens(String access, String refresh) async {
    await _storage.write(key: _accessKey, value: access);
    await _storage.write(key: _refreshKey, value: refresh);
  }

  Future<void> clearTokens() async {
    await _storage.delete(key: _accessKey);
    await _storage.delete(key: _refreshKey);
  }

  Future<bool> hasSession() async {
    return await _storage.read(key: _accessKey) != null;
  }

  Future<http.Response> _request(
    String method,
    String path, {
    required bool auth,
    Map<String, dynamic>? body,
    bool binary = false,
  }) async {
    for (var attempt = 0; attempt <= _networkRetryDelays.length; attempt++) {
      try {
        return await _performRequest(
          method,
          path,
          auth: auth,
          body: body,
          binary: binary,
        );
      } on ApiException {
        rethrow;
      } on TimeoutException {
        // Réessai progressif, notamment pendant le réveil de Render.
      } on http.ClientException {
        // Réessai progressif sur les erreurs réseau navigateur/mobile.
      } catch (e) {
        if (isNetworkError(e)) {
          // Réessai progressif sur toute autre erreur réseau reconnue.
        } else {
          rethrow;
        }
      }

      if (attempt < _networkRetryDelays.length) {
        await Future<void>.delayed(_networkRetryDelays[attempt]);
        continue;
      }
    }

    throw ApiException(
      friendlyNetworkError(serverWaking: ApiConfig.isProductionDeployment),
    );
  }

  Future<http.Response> _performRequest(
    String method,
    String path, {
    required bool auth,
    Map<String, dynamic>? body,
    bool binary = false,
  }) async {
    final uri = Uri.parse('${ApiConfig.baseUrl}$path');
    final headers = await _headers(auth: auth, binary: binary);

    http.Response response;
    response = await _send(
      method,
      uri,
      headers: headers,
      body: body,
    );

    if (response.statusCode == 401 && auth) {
      final refreshed = await _refreshAccessToken();
      if (refreshed) {
        final retryHeaders = await _headers(auth: true, binary: binary);
        response = await _send(
          method,
          uri,
          headers: retryHeaders,
          body: body,
        );
      }
    }

    return response;
  }

  Future<http.Response> _send(
    String method,
    Uri uri, {
    required Map<String, String> headers,
    Map<String, dynamic>? body,
  }) {
    final encodedBody = body == null ? null : jsonEncode(body);
    return switch (method) {
      'GET' => http.get(uri, headers: headers).timeout(_requestTimeout),
      'PATCH' => http
          .patch(uri, headers: headers, body: encodedBody)
          .timeout(_requestTimeout),
      _ => http
          .post(uri, headers: headers, body: encodedBody)
          .timeout(_requestTimeout),
    };
  }

  Future<bool> _refreshAccessToken() async {
    final refresh = await _storage.read(key: _refreshKey);
    if (refresh == null) return false;

    try {
      final response = await http
          .post(
            Uri.parse('${ApiConfig.baseUrl}/auth/refresh/'),
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
            },
            body: jsonEncode({'refresh_token': refresh}),
          )
          .timeout(_requestTimeout);

      if (response.statusCode != 200) {
        await clearTokens();
        return false;
      }

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      await saveTokens(
        data['access_token'] as String,
        data['refresh_token'] as String,
      );
      return true;
    } on TimeoutException {
      await clearTokens();
      return false;
    }
  }

  Map<String, dynamic> decodeMap(http.Response response, {bool notify = true}) {
    if (response.statusCode >= 400) {
      if (notify) {
        _notifyHttpError(response.statusCode);
      }
      throw ApiException(
        friendlyHttpError(response.statusCode, response.body),
        statusCode: response.statusCode,
      );
    }
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  List<dynamic> decodeList(http.Response response, {bool notify = true}) {
    if (response.statusCode >= 400) {
      if (notify) {
        _notifyHttpError(response.statusCode);
      }
      throw ApiException(
        friendlyHttpError(response.statusCode, response.body),
        statusCode: response.statusCode,
      );
    }

    final decoded = jsonDecode(response.body);
    if (decoded is List) return decoded;
    if (decoded is Map<String, dynamic> && decoded.containsKey('items')) {
      return decoded['items'] as List<dynamic>;
    }
    return const [];
  }

  List<dynamic> decodeJsonList(http.Response response, {bool notify = true}) {
    if (response.statusCode >= 400) {
      if (notify) {
        _notifyHttpError(response.statusCode);
      }
      throw ApiException(
        friendlyHttpError(response.statusCode, response.body),
        statusCode: response.statusCode,
      );
    }
    final decoded = jsonDecode(response.body);
    if (decoded is List) {
      return decoded;
    }
    return const [];
  }

  Future<void> _notifyHttpError(int statusCode) async {
    if (statusCode == 401) {
      if (await hasSession()) {
        ApiSession.onSessionExpired?.call();
      }
      return;
    }
    if (statusCode == 403) {
      ApiSession.onForbidden?.call(
        friendlyHttpError(statusCode, '', isPatient: ApiSession.isPatient),
      );
    }
  }
}
