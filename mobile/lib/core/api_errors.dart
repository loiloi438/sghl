import 'api_client.dart';

String friendlyApiError(Object error) {
  if (error is ApiException) return error.message;
  final text = error.toString();
  if (text.startsWith('ApiException:')) {
    return text.replaceFirst('ApiException:', '').trim();
  }
  return text;
}
