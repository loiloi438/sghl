import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../core/sghl_theme.dart';
import 'human_care_widgets.dart';
import 'sghl_design_system.dart';

/// Mise en page premium Human-Care pour connexion / inscription (web + mobile).
class SghlHumanCareAuthLayout extends StatelessWidget {
  const SghlHumanCareAuthLayout({
    super.key,
    required this.title,
    required this.subtitle,
    required this.child,
    this.loading = false,
    this.leading,
  });

  final String title;
  final String subtitle;
  final Widget child;
  final bool loading;
  final Widget? leading;

  static const welcomeSubtitle =
      'Accédez à votre espace santé — simple, rassurant et sécurisé 💙';

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        SghlHumanCareBackground(
          child: SafeArea(
            child: Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(20, 24, 20, 40),
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 440),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      if (leading != null) ...[
                        Align(alignment: Alignment.centerLeft, child: leading!),
                        const SizedBox(height: 8),
                      ],
                      const _TrustIconRow(),
                      const SizedBox(height: 20),
                      SghlCard(
                        lightSurface: true,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            Text(
                              '🌿 Human-Care',
                              style: GoogleFonts.nunito(
                                fontSize: 13,
                                fontWeight: FontWeight.w800,
                                color: SghlColors.humanCareTeal,
                                letterSpacing: 0.4,
                              ),
                            ),
                            const SizedBox(height: 10),
                            Text(
                              title,
                              style: GoogleFonts.poppins(
                                fontSize: 24,
                                fontWeight: FontWeight.w800,
                                color: SghlColors.humanCareText,
                                height: 1.2,
                              ),
                            ),
                            const SizedBox(height: 10),
                            Text(
                              subtitle,
                              style: GoogleFonts.nunito(
                                fontSize: 15,
                                fontWeight: FontWeight.w600,
                                color: SghlColors.humanCareMuted,
                                height: 1.45,
                              ),
                            ),
                            const SizedBox(height: 22),
                            child,
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
        if (loading) const SghlHumanCareLoadingOverlay(),
      ],
    );
  }
}

class _TrustIconRow extends StatelessWidget {
  const _TrustIconRow();

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: const [
        _TrustBadge(
          icon: Icons.favorite_rounded,
          color: Color(0xFF34D399),
          label: 'Soin',
        ),
        SizedBox(width: 12),
        _TrustBadge(
          icon: Icons.medical_services_outlined,
          color: Color(0xFF38BDF8),
          label: 'Médical',
        ),
        SizedBox(width: 12),
        _TrustBadge(
          icon: Icons.person_outline_rounded,
          color: Color(0xFF0D9488),
          label: 'Patient',
        ),
      ],
    );
  }
}

class _TrustBadge extends StatelessWidget {
  const _TrustBadge({
    required this.icon,
    required this.color,
    required this.label,
  });

  final IconData icon;
  final Color color;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          width: 52,
          height: 52,
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.92),
            shape: BoxShape.circle,
            border: Border.all(color: color.withValues(alpha: 0.35)),
            boxShadow: [
              BoxShadow(
                color: color.withValues(alpha: 0.18),
                blurRadius: 12,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Icon(icon, color: color, size: 24),
        ),
        const SizedBox(height: 6),
        Text(
          label,
          style: GoogleFonts.nunito(
            fontSize: 11,
            fontWeight: FontWeight.w700,
            color: SghlColors.humanCareMuted,
          ),
        ),
      ],
    );
  }
}

/// Overlay de chargement doux pendant les appels API.
class SghlHumanCareLoadingOverlay extends StatelessWidget {
  const SghlHumanCareLoadingOverlay({super.key});

  @override
  Widget build(BuildContext context) {
    return AbsorbPointer(
      child: Container(
        color: const Color(0xFFF0FDF9).withValues(alpha: 0.72),
        alignment: Alignment.center,
        child: const _PulsingCareLoader(),
      ),
    );
  }
}

class _PulsingCareLoader extends StatefulWidget {
  const _PulsingCareLoader();

  @override
  State<_PulsingCareLoader> createState() => _PulsingCareLoaderState();
}

class _PulsingCareLoaderState extends State<_PulsingCareLoader>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1400),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        final scale = 0.92 + (_controller.value * 0.08);
        return Transform.scale(
          scale: scale,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 22),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(24),
              border: Border.all(color: const Color(0xFFA7F3D0)),
              boxShadow: [
                BoxShadow(
                  color: SghlColors.humanCareMint.withValues(alpha: 0.25),
                  blurRadius: 24,
                  offset: const Offset(0, 8),
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                SizedBox(
                  width: 36,
                  height: 36,
                  child: CircularProgressIndicator(
                    strokeWidth: 3,
                    color: SghlColors.humanCareTeal.withValues(
                      alpha: 0.65 + (_controller.value * 0.35),
                    ),
                  ),
                ),
                const SizedBox(height: 14),
                Text(
                  'Connexion sécurisée en cours…',
                  style: GoogleFonts.nunito(
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                    color: SghlColors.humanCareText,
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
