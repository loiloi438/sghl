import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

import 'api_config.dart';

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

  Future<Map<String, String>> _headers({bool auth = true, bool binary = false}) async {
    final headers = <String, String>{};
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

  Future<List<int>> downloadBytes(String path, {bool auth = true}) async {
    final response = await _request('GET', path, auth: auth, binary: true);
    if (response.statusCode >= 400) {
      String message = 'Erreur serveur (${response.statusCode})';
      try {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        message = (data['detail'] ?? data['message'] ?? message).toString();
      } catch (_) {}
      throw ApiException(message, statusCode: response.statusCode);
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
    final uri = Uri.parse('${ApiConfig.baseUrl}$path');
    final headers = await _headers(auth: auth, binary: binary);

    http.Response response;
    if (method == 'GET') {
      response = await http.get(uri, headers: headers);
    } else {
      response = await http.post(uri, headers: headers, body: jsonEncode(body));
    }

    if (response.statusCode == 401 && auth) {
      final refreshed = await _refreshAccessToken();
      if (refreshed) {
        final retryHeaders = await _headers(auth: true, binary: binary);
        if (method == 'GET') {
          response = await http.get(uri, headers: retryHeaders);
        } else {
          response = await http.post(
            uri,
            headers: retryHeaders,
            body: jsonEncode(body),
          );
        }
      }
    }

    return response;
  }

  Future<bool> _refreshAccessToken() async {
    final refresh = await _storage.read(key: _refreshKey);
    if (refresh == null) return false;

    final response = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/auth/refresh/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'refresh_token': refresh}),
    );

    if (response.statusCode != 200) {
      await clearTokens();
      return false;
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    await saveTokens(data['access_token'] as String, data['refresh_token'] as String);
    return true;
  }

  Map<String, dynamic> decodeMap(http.Response response) {
    if (response.statusCode >= 400) {
      String message = 'Erreur serveur (${response.statusCode})';
      try {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        message = (data['detail'] ?? data['message'] ?? message).toString();
      } catch (_) {}
      throw ApiException(message, statusCode: response.statusCode);
    }
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  List<dynamic> decodeList(http.Response response) {
    final data = decodeMap(response);
    if (data.containsKey('items')) {
      return data['items'] as List<dynamic>;
    }
    return const [];
  }

  /// Réponse API en tableau JSON (ex. `/rendez-vous/semaine/`).
  List<dynamic> decodeJsonList(http.Response response) {
    if (response.statusCode >= 400) {
      String message = 'Erreur serveur (${response.statusCode})';
      try {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        message = (data['detail'] ?? data['message'] ?? message).toString();
      } catch (_) {}
      throw ApiException(message, statusCode: response.statusCode);
    }
    final decoded = jsonDecode(response.body);
    if (decoded is List) {
      return decoded;
    }
    return const [];
  }
}
