import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';

import 'core/sghl_page_route.dart';
import 'core/sghl_theme.dart';
import 'core/theme_notifier.dart';
import 'services/patient_services.dart';
import 'screens/constantes_screen.dart';
import 'screens/doses_screen.dart';
import 'screens/factures_screen.dart';
import 'screens/home_screen.dart';
import 'screens/laboratoire_screen.dart';
import 'screens/login_screen.dart';
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

    return MaterialApp(
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
    );
  }

  static Route<dynamic>? _onGenerateRoute(RouteSettings settings) {
    final Widget page = switch (settings.name) {
      LoginScreen.route => const LoginScreen(),
      RegisterScreen.route => const RegisterScreen(),
      ValidateAccountScreen.route => ValidateAccountScreen(
          initialUsername: settings.arguments as String? ?? '',
        ),
      PatientShell.route => const PatientShell(),
      HomeScreen.route => const HomeScreen(),
      ConstantesScreen.route => const ConstantesScreen(),
      PlansScreen.route => const PlansScreen(),
      DosesScreen.route => const DosesScreen(),
      PrescriptionsScreen.route => const PrescriptionsScreen(),
      LaboratoireScreen.route => const LaboratoireScreen(),
      FacturesScreen.route => const FacturesScreen(),
      RendezVousScreen.route => const RendezVousScreen(),
      NotificationsScreen.route => const NotificationsScreen(),
      ProfilScreen.route => const ProfilScreen(),
      StaffHomeScreen.route => const StaffHomeScreen(),
      StaffRendezVousScreen.route => const StaffRendezVousScreen(),
      _ => throw Exception('Route inconnue: ${settings.name}'),
    };

    if (_instantRoutes.contains(settings.name)) {
      return MaterialPageRoute<void>(
        builder: (_) => page,
        settings: settings,
      );
    }

    return SghlSlideUpRoute<void>(page: page, settings: settings);
  }
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
    await context.read<ThemeNotifier>().load();
    final auth = context.read<AuthService>();
    final ok = await auth.tryRestoreSession();
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
