import '../screens/login_screen.dart';
import '../screens/patient_shell.dart';
import '../screens/staff_home_screen.dart';
import '../screens/staff_rendez_vous_screen.dart';
import '../services/patient_services.dart';

class RoleGuardResult {
  const RoleGuardResult(this.route, {this.message});

  final String route;
  final String? message;
}

/// Garde de navigation selon le rôle connecté.
class RoleGuard {
  RoleGuard._();

  static const publicRoutes = {
    LoginScreen.route,
    '/register',
    '/validate-account',
  };

  static const staffRoutes = {
    StaffHomeScreen.route,
    StaffRendezVousScreen.route,
  };

  static bool isPublic(String? route) => publicRoutes.contains(route);

  static bool isStaffRoute(String? route) => staffRoutes.contains(route);

  static bool isPatientExperienceRoute(String? route) {
    if (route == null || isPublic(route) || isStaffRoute(route)) return false;
    return route.startsWith('/');
  }

  static RoleGuardResult resolve({
    required String? requestedRoute,
    required AuthService auth,
  }) {
    if (requestedRoute == null || isPublic(requestedRoute)) {
      return RoleGuardResult(requestedRoute ?? LoginScreen.route);
    }

    if (!auth.isAuthenticated) {
      return const RoleGuardResult(LoginScreen.route);
    }

    if (auth.isPatient && isStaffRoute(requestedRoute)) {
      return const RoleGuardResult(
        PatientShell.route,
        message: 'Cette fonctionnalité est réservée au personnel médical 💙',
      );
    }

    if (!auth.isPatient && isPatientExperienceRoute(requestedRoute)) {
      return RoleGuardResult(
        StaffHomeScreen.route,
        message: 'Espace réservé aux patients.',
      );
    }

    return RoleGuardResult(requestedRoute);
  }
}
