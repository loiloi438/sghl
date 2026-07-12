import 'package:flutter/material.dart';

import '../core/sghl_theme.dart';
import '../widgets/sghl_design_system.dart';
import 'home_screen.dart';
import 'messagerie_screen.dart';
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
    ),
    SghlNavItem(
      icon: Icons.folder_outlined,
      selectedIcon: Icons.folder_rounded,
    ),
    SghlNavItem(
      icon: Icons.chat_bubble_outline_rounded,
      selectedIcon: Icons.chat_bubble_rounded,
    ),
    SghlNavItem(
      icon: Icons.person_outline_rounded,
      selectedIcon: Icons.person_rounded,
    ),
  ];

  static const _pages = [
    HomeScreen(embedded: true),
    RendezVousScreen(embedded: true),
    MessagerieScreen(embedded: true),
    ProfilScreen(embedded: true),
  ];

  @override
  Widget build(BuildContext context) {
    return Theme(
      data: SghlTheme.patientHumanCare(),
      child: Scaffold(        body: Stack(
          children: [
            Positioned.fill(
              child: AnimatedSwitcher(
                duration: const Duration(milliseconds: 320),
                switchInCurve: Curves.easeOutCubic,
                switchOutCurve: Curves.easeInCubic,
                transitionBuilder: (child, animation) {
                  return FadeTransition(
                    opacity: animation,
                    child: SlideTransition(
                      position: Tween<Offset>(
                        begin: const Offset(0, 0.03),
                        end: Offset.zero,
                      ).animate(animation),
                      child: child,
                    ),
                  );
                },
                child: KeyedSubtree(
                  key: ValueKey<int>(_index),
                  child: _pages[_index],
                ),
              ),
            ),
            Positioned(
              left: 0,
              right: 0,
              bottom: 12,
              child: SafeArea(
                top: false,
                child: SghlFloatingNavBar(
                  items: _navItems,
                  selectedIndex: _index,
                  onSelected: (i) => setState(() => _index = i),
                  lightBar: true,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
