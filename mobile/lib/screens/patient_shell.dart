import 'package:flutter/material.dart';

import '../core/sghl_theme.dart';
import '../widgets/sghl_design_system.dart';
import 'home_screen.dart';
import 'prescriptions_screen.dart';
import 'profil_screen.dart';
import 'rendez_vous_screen.dart';

class PatientShell extends StatefulWidget {
  const PatientShell({super.key});

  static const route = '/patient-shell';

  @override
  State<PatientShell> createState() => _PatientShellState();
}

class _PatientShellState extends State<PatientShell> {
  int _index = 0;

  static const _navItems = [
    SghlNavItem(
      icon: Icons.home_outlined,
      selectedIcon: Icons.home_rounded,
      label: 'Accueil',
    ),
    SghlNavItem(
      icon: Icons.calendar_month_outlined,
      selectedIcon: Icons.calendar_month_rounded,
      label: 'Rendez-vous',
    ),
    SghlNavItem(
      icon: Icons.medication_outlined,
      selectedIcon: Icons.medication_rounded,
      label: 'Ordonnances',
    ),
    SghlNavItem(
      icon: Icons.person_outline_rounded,
      selectedIcon: Icons.person_rounded,
      label: 'Mon profil',
    ),
  ];

  static const _pages = [
    HomeScreen(embedded: true),
    RendezVousScreen(embedded: true),
    PrescriptionsScreen(),
    ProfilScreen(embedded: true),
  ];

  @override
  Widget build(BuildContext context) {
    return Theme(
      data: SghlTheme.patientHumanCare(),
      child: Scaffold(
        body: Stack(
          children: [
            Positioned.fill(
              child: IndexedStack(index: _index, children: _pages),
            ),
            Positioned(
              left: 0,
              right: 0,
              bottom: 0,
              child: SafeArea(
                top: false,
                child: SghlFloatingNavBar(
                  items: _navItems,
                  selectedIndex: _index,
                  onSelected: (i) => setState(() => _index = i),
                  lightBar: true,
                  compact: false,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
