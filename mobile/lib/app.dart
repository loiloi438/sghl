import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';

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
      routes: {
        LoginScreen.route: (_) => const LoginScreen(),
        RegisterScreen.route: (_) => const RegisterScreen(),
        ValidateAccountScreen.route: (ctx) {
          final username = ModalRoute.of(ctx)?.settings.arguments as String? ?? '';
          return ValidateAccountScreen(initialUsername: username);
        },
        PatientShell.route: (_) => const PatientShell(),
        HomeScreen.route: (_) => const HomeScreen(),
        ConstantesScreen.route: (_) => const ConstantesScreen(),
        PlansScreen.route: (_) => const PlansScreen(),
        DosesScreen.route: (_) => const DosesScreen(),
        PrescriptionsScreen.route: (_) => const PrescriptionsScreen(),
        LaboratoireScreen.route: (_) => const LaboratoireScreen(),
        FacturesScreen.route: (_) => const FacturesScreen(),
        RendezVousScreen.route: (_) => const RendezVousScreen(),
        NotificationsScreen.route: (_) => const NotificationsScreen(),
        ProfilScreen.route: (_) => const ProfilScreen(),
        StaffHomeScreen.route: (_) => const StaffHomeScreen(),
        StaffRendezVousScreen.route: (_) => const StaffRendezVousScreen(),
      },
    );
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
