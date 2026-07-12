import 'dart:html' as html;

bool get isLocalWebHost {
  final host = html.window.location.hostname.toLowerCase();
  return host.isEmpty || host == 'localhost' || host == '127.0.0.1';
}

String get currentWebHostname => html.window.location.hostname.toLowerCase();

String? readWebConfiguredApiBaseUrl() {
  final meta = html.document.querySelector('meta[name="sghl-api-base"]');
  final value = meta?.getAttribute('content')?.trim();
  if (value != null && value.isNotEmpty) return value;
  return null;
}
