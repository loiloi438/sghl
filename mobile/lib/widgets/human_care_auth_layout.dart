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
                      const SghlHumanCareLogo(),
                      const SizedBox(height: 24),
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

/// Logo vectoriel commun à l'accueil et à l'espace patient.
class SghlHumanCareLogo extends StatelessWidget {
  const SghlHumanCareLogo({super.key, this.compact = false});

  final bool compact;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: compact
          ? MainAxisAlignment.start
          : MainAxisAlignment.center,
      mainAxisSize: MainAxisSize.max,
      children: [
        Container(
          width: compact ? 46 : 64,
          height: compact ? 46 : 64,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [Color(0xFF2DD4BF), Color(0xFF0891B2)],
            ),
            borderRadius: BorderRadius.circular(compact ? 16 : 22),
            boxShadow: [
              BoxShadow(
                color: SghlColors.humanCareTeal.withValues(alpha: 0.22),
                blurRadius: 22,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          child: Stack(
            alignment: Alignment.center,
            children: [
              Icon(
                Icons.favorite_rounded,
                color: Colors.white,
                size: compact ? 29 : 42,
              ),
              Positioned(
                top: compact ? 7 : 9,
                right: compact ? 6 : 8,
                child: Icon(
                  Icons.add_rounded,
                  color: Colors.white,
                  size: compact ? 15 : 20,
                ),
              ),
            ],
          ),
        ),
        SizedBox(width: compact ? 10 : 14),
        Flexible(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'SGHL',
                maxLines: 1,
                style: GoogleFonts.poppins(
                  color: SghlColors.humanCareText,
                  fontWeight: FontWeight.w800,
                  fontSize: compact ? 25 : 38,
                  letterSpacing: 0.4,
                ),
              ),
              Text(
                compact
                    ? 'Message Portal Hospitalier'
                    : 'Pour votre santé et bien-être',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: GoogleFonts.nunito(
                  color: SghlColors.humanCareMuted,
                  fontWeight: FontWeight.w600,
                  fontSize: compact ? 11 : 13,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

/// Illustration 100 % vectorielle, légère et disponible hors connexion.
class SghlMedicalWelcomeIllustration extends StatelessWidget {
  const SghlMedicalWelcomeIllustration({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 205,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(32),
        gradient: const LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [Color(0xFFE0F7FA), Color(0xFFECFDF5)],
        ),
      ),
      child: Stack(
        alignment: Alignment.bottomCenter,
        children: [
          Positioned(
            top: 26,
            left: 48,
            right: 48,
            child: Container(
              height: 112,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(22),
                border: Border.all(color: const Color(0xFFBAE6FD)),
                boxShadow: [
                  BoxShadow(
                    color: const Color(0xFF0891B2).withValues(alpha: 0.10),
                    blurRadius: 20,
                    offset: const Offset(0, 8),
                  ),
                ],
              ),
              child: const Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.local_hospital_rounded,
                    color: SghlColors.humanCareTeal,
                    size: 42,
                  ),
                  SizedBox(height: 4),
                  Text(
                    'CENTRE HOSPITALIER SGHL',
                    style: TextStyle(
                      color: SghlColors.humanCareText,
                      fontSize: 10,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.5,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const Positioned(
            left: 22,
            bottom: 20,
            child: _CareProfessional(icon: Icons.person_rounded),
          ),
          const Positioned(
            right: 22,
            bottom: 20,
            child: _CareProfessional(icon: Icons.person_2_rounded),
          ),
          Positioned(
            bottom: 8,
            child: Container(
              width: 150,
              height: 24,
              decoration: BoxDecoration(
                color: const Color(0xFF6EE7B7).withValues(alpha: 0.35),
                borderRadius: BorderRadius.circular(999),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _CareProfessional extends StatelessWidget {
  const _CareProfessional({required this.icon});

  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 82,
      height: 100,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: const BorderRadius.vertical(
          top: Radius.circular(42),
          bottom: Radius.circular(18),
        ),
        boxShadow: [
          BoxShadow(
            color: SghlColors.humanCareTeal.withValues(alpha: 0.14),
            blurRadius: 16,
            offset: const Offset(0, 7),
          ),
        ],
      ),
      child: Stack(
        alignment: Alignment.center,
        children: [
          Icon(icon, size: 54, color: const Color(0xFF7DD3FC)),
          const Positioned(
            bottom: 12,
            child: Icon(
              Icons.medical_services_outlined,
              size: 24,
              color: SghlColors.humanCareTeal,
            ),
          ),
        ],
      ),
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
