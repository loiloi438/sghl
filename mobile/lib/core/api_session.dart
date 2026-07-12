/// Contexte session API (rôle courant + callbacks globaux).
class ApiSession {
  ApiSession._();

  static bool isPatient = false;

  static void Function()? onSessionExpired;
  static void Function(String message)? onForbidden;

  static void reset() {
    isPatient = false;
    onSessionExpired = null;
    onForbidden = null;
  }
}
