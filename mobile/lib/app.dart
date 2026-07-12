import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';

import 'core/api_config.dart';
import 'core/api_session.dart';
import 'core/role_guard.dart';
import 'core/api_client.dart';
import 'core/sghl_page_route.dart';
import 'core/sghl_theme.dart';
import 'core/theme_notifier.dart';
import 'services/patient_services.dart';
import 'screens/constantes_screen.dart';
import 'screens/doses_screen.dart';
import 'screens/factures_screen.dart';
import 'screens/home_screen.dart';
import 'screens/hospitalisations_screen.dart';
import 'screens/laboratoire_screen.dart';
import 'screens/login_screen.dart';
import 'screens/messagerie_screen.dart';
import 'screens/patient_shell.dart';
import 'screens/plans_screen.dart';
import 'screens/prescriptions_screen.dart';
import 'screens/notifications_screen.dart';
import 'screens/profil_screen.dart';
import 'screens/register_screen.dart';
import 'screens/rendez_vous_screen.dart';
import 'screens/staff_home_screen.dart';
import 'screens/staff_rendez_vous_screen.dart';
import 'screens/validate_account_screen.dart';
import 'widgets/patient_human_care_page.dart';

class SghlApp extends StatelessWidget {
  const SghlApp({super.key});

  static const _instantRoutes = {
    LoginScreen.route,
    RegisterScreen.route,
    ValidateAccountScreen.route,
    PatientShell.route,
    StaffHomeScreen.route,
  };

  @override
  Widget build(BuildContext context) {
    final themeNotifier = context.watch<ThemeNotifier>();

    return _ApiSessionScope(
      child: MaterialApp(
        title: 'SGHL Mobile',
        debugShowCheckedModeBanner: false,
        locale: const Locale('fr', 'FR'),
        supportedLocales: const [Locale('fr', 'FR')],
        localizationsDelegates: const [
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        theme: SghlTheme.light(),
        darkTheme: SghlTheme.dark(),
        themeMode: themeNotifier.mode,
        home: const _RootScreen(),
        onGenerateRoute: _onGenerateRoute,
      ),
    );
  }

  static const _patientThemedRoutes = {
    RegisterScreen.route,
    ValidateAccountScreen.route,
    PatientShell.route,
    HomeScreen.route,
    HospitalisationsScreen.route,
    ConstantesScreen.route,
    PlansScreen.route,
    DosesScreen.route,
    PrescriptionsScreen.route,
    LaboratoireScreen.route,
    FacturesScreen.route,
    RendezVousScreen.route,
    MessagerieScreen.route,
    NotificationsScreen.route,
    ProfilScreen.route,
  };

  static Widget _withPatientTheme(String? routeName, Widget page) {
    if (_patientThemedRoutes.contains(routeName)) {
      return PatientHumanCareTheme(child: page);
    }
    return page;
  }

  static Widget _buildPage(String? routeName, RouteSettings settings) {
    return switch (routeName) {
      LoginScreen.route => const LoginScreen(),
      RegisterScreen.route => const RegisterScreen(),
      ValidateAccountScreen.route => ValidateAccountScreen(
          initialUsername: (settings.arguments as Map?)?['username'] as String? ??
              settings.arguments as String? ??
              '',
          initialCode: (settings.arguments as Map?)?['code'] as String? ?? '',
        ),
      PatientShell.route => const PatientShell(),
      HomeScreen.route => const HomeScreen(),
      HospitalisationsScreen.route => const HospitalisationsScreen(),
      ConstantesScreen.route => const ConstantesScreen(),
      PlansScreen.route => const PlansScreen(),
      DosesScreen.route => const DosesScreen(),
      PrescriptionsScreen.route => const PrescriptionsScreen(),
      LaboratoireScreen.route => const LaboratoireScreen(),
      FacturesScreen.route => const FacturesScreen(),
      RendezVousScreen.route => const RendezVousScreen(),
      MessagerieScreen.route => const MessagerieScreen(),
      NotificationsScreen.route => const NotificationsScreen(),
      ProfilScreen.route => const ProfilScreen(),
      StaffHomeScreen.route => const StaffHomeScreen(),
      StaffRendezVousScreen.route => const StaffRendezVousScreen(),
      _ => throw Exception('Route inconnue: $routeName'),
    };
  }

  static Route<dynamic>? _onGenerateRoute(RouteSettings settings) {
    Widget buildGuardedPage(BuildContext context) {
      final auth = context.read<AuthService>();
      final guard = RoleGuard.resolve(
        requestedRoute: settings.name,
        auth: auth,
      );

      if (guard.route != settings.name && guard.message != null) {
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (!context.mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(guard.message!)),
          );
        });
      }

      final page = _buildPage(guard.route, settings);
      return _withPatientTheme(guard.route, page);
    }

    if (_instantRoutes.contains(settings.name)) {
      return MaterialPageRoute<void>(
        builder: buildGuardedPage,
        settings: settings,
      );
    }

    return SghlSlideUpRoute<void>(
      page: Builder(builder: buildGuardedPage),
      settings: settings,
    );
  }
}

/// Branche les callbacks 401/403 et synchronise le rôle patient.
class _ApiSessionScope extends StatefulWidget {
  const _ApiSessionScope({required this.child});

  final Widget child;

  @override
  State<_ApiSessionScope> createState() => _ApiSessionScopeState();
}

class _ApiSessionScopeState extends State<_ApiSessionScope> {
  bool _handlingSession = false;

  @override
  void initState() {
    super.initState();
    final auth = context.read<AuthService>();
    _syncRole(auth);
    auth.addListener(_onAuthChanged);
    ApiSession.onSessionExpired = _onSessionExpired;
    ApiSession.onForbidden = _onForbidden;
  }

  @override
  void dispose() {
    context.read<AuthService>().removeListener(_onAuthChanged);
    ApiSession.reset();
    super.dispose();
  }

  void _onAuthChanged() => _syncRole(context.read<AuthService>());

  void _syncRole(AuthService auth) {
    ApiSession.isPatient = auth.isPatient;
  }

  Future<void> _onSessionExpired() async {
    if (_handlingSession || !mounted) return;
    _handlingSession = true;
    try {
      await context.read<AuthService>().logout();
      if (!mounted) return;
      Navigator.of(context).pushNamedAndRemoveUntil(
        LoginScreen.route,
        (_) => false,
      );
    } finally {
      _handlingSession = false;
    }
  }

  void _onForbidden(String message) {
    if (!mounted || !ApiSession.isPatient) return;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );
      Navigator.of(context).pushNamedAndRemoveUntil(
        PatientShell.route,
        (_) => false,
      );
    });
  }

  @override
  Widget build(BuildContext context) => widget.child;
}

class _RootScreen extends StatefulWidget {
  const _RootScreen();

  @override
  State<_RootScreen> createState() => _RootScreenState();
}

class _RootScreenState extends State<_RootScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _bootstrap());
  }

  Future<void> _bootstrap() async {
    final themeNotifier = context.read<ThemeNotifier>();
    final auth = context.read<AuthService>();
    final api = context.read<ApiClient>();
    await themeNotifier.load();

    if (ApiConfig.isProductionDeployment) {
      try {
        await api.warmUp();
      } catch (_) {}
    }

    var ok = false;
    try {
      ok = await auth.tryRestoreSession().timeout(const Duration(seconds: 15));
    } catch (_) {
      ok = false;
    }
    if (!mounted) return;
    final home = ok
        ? (auth.isPatient ? PatientShell.route : StaffHomeScreen.route)
        : LoginScreen.route;
    Navigator.of(context).pushReplacementNamed(home);
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(child: CircularProgressIndicator()),
    );
  }
}
