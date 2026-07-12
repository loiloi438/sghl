import 'dart:html' as html;

String _normalizedHost() =>
    (html.window.location.hostname ?? '').toLowerCase();

bool get isLocalWebHost {
  final host = _normalizedHost();
  return host.isEmpty || host == 'localhost' || host == '127.0.0.1';
}

String get currentWebHostname => _normalizedHost();

String? readWebConfiguredApiBaseUrl() {
  final meta = html.document.querySelector('meta[name="sghl-api-base"]');
  final value = meta?.getAttribute('content')?.trim();
  if (value != null && value.isNotEmpty) return value;
  return null;
}
