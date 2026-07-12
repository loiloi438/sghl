import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../core/sghl_theme.dart';

/// Bouton vert pastel Human-Care (« Prendre rendez-vous »).
class SghlHumanCareButton extends StatelessWidget {
  const SghlHumanCareButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.loading = false,
    this.icon,
    this.compact = false,
  });

  final String label;
  final VoidCallback? onPressed;
  final bool loading;
  final IconData? icon;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        gradient: SghlColors.humanCareCtaGradient,
        borderRadius: BorderRadius.circular(compact ? 999 : 999),
        boxShadow: [
          BoxShadow(
            color: SghlColors.humanCareMint.withValues(alpha: 0.35),
            blurRadius: 14,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: loading ? null : onPressed,
          borderRadius: BorderRadius.circular(999),
          child: Container(
            width: compact ? null : double.infinity,
            padding: EdgeInsets.symmetric(
              horizontal: compact ? 20 : 24,
              vertical: compact ? 12 : 14,
            ),
            alignment: compact ? null : Alignment.center,
            child: loading
                ? const SizedBox(
                    height: 22,
                    width: 22,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Color(0xFF064E3B),
                    ),
                  )
                : Row(
                    mainAxisSize:
                        compact ? MainAxisSize.min : MainAxisSize.max,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      if (icon != null) ...[
                        Icon(icon, color: const Color(0xFF064E3B), size: 20),
                        const SizedBox(width: 8),
                      ],
                      Text(
                        label,
                        style: GoogleFonts.poppins(
                          color: const Color(0xFF064E3B),
                          fontWeight: FontWeight.w700,
                          fontSize: compact ? 14 : 16,
                        ),
                      ),
                    ],
                  ),
          ),
        ),
      ),
    );
  }
}

/// Carte KPI pastel (tableau de bord patient).
class SghlHumanCareStatCard extends StatelessWidget {
  const SghlHumanCareStatCard({
    super.key,
    required this.value,
    required this.label,
    this.detail,
    this.icon,
    this.backgroundColor = const Color(0xFFECFDF5),
    this.borderColor = const Color(0xFFA7F3D0),
    this.labelColor = const Color(0xFF0D9488),
  });

  final String value;
  final String label;
  final String? detail;
  final IconData? icon;
  final Color backgroundColor;
  final Color borderColor;
  final Color labelColor;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 12),
        decoration: BoxDecoration(
          color: backgroundColor,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: borderColor),
          boxShadow: [
            BoxShadow(
              color: borderColor.withValues(alpha: 0.35),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (icon != null)
              Icon(icon, size: 18, color: labelColor),
            if (icon != null) const SizedBox(height: 6),
            Text(
              value,
              style: GoogleFonts.poppins(
                fontSize: 20,
                fontWeight: FontWeight.w800,
                color: const Color(0xFF134E4A),
              ),
            ),
            const SizedBox(height: 2),
            Text(
              label,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: GoogleFonts.nunito(
                fontSize: 11,
                fontWeight: FontWeight.w800,
                letterSpacing: 0.8,
                color: labelColor,
              ),
            ),
            if (detail != null) ...[
              const SizedBox(height: 4),
              Text(
                detail!,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: GoogleFonts.nunito(
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                  color: SghlColors.humanCareMuted,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// Bandeau message bienveillant.
class SghlHumanCareWellnessBanner extends StatelessWidget {
  const SghlHumanCareWellnessBanner({super.key, required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.85),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFA7F3D0)),
      ),
      child: Text(
        message,
        style: GoogleFonts.nunito(
          fontSize: 14,
          fontWeight: FontWeight.w700,
          color: const Color(0xFF115E59),
          height: 1.4,
        ),
      ),
    );
  }
}

/// En-tête Human-Care avec tagline.
class SghlHumanCareHero extends StatelessWidget {
  const SghlHumanCareHero({
    super.key,
    required this.prenom,
    this.wellnessMessage,
    this.trailing,
  });

  final String prenom;
  final String? wellnessMessage;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) {
    final greeting =
        prenom.isNotEmpty ? 'Bonjour $prenom 👋' : 'Bonjour 👋';

    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 52, 20, 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '🌿 Human-Care',
                      style: GoogleFonts.nunito(
                        fontSize: 13,
                        fontWeight: FontWeight.w800,
                        color: const Color(0xFF0D9488),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      greeting,
                      style: GoogleFonts.poppins(
                        fontSize: 24,
                        fontWeight: FontWeight.w700,
                        color: const Color(0xFF134E4A),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Pour votre santé et bien-être',
                      style: GoogleFonts.nunito(
                        fontSize: 14,
                        fontWeight: FontWeight.w500,
                        color: SghlColors.humanCareMuted,
                      ),
                    ),
                  ],
                ),
              ),
              if (trailing != null) trailing!,
            ],
          ),
          if (wellnessMessage != null && wellnessMessage!.isNotEmpty) ...[
            const SizedBox(height: 12),
            SghlHumanCareWellnessBanner(message: wellnessMessage!),
          ],
        ],
      ),
    );
  }
}

/// Fond dégradé pastel Human-Care.
class SghlHumanCareBackground extends StatelessWidget {
  const SghlHumanCareBackground({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(gradient: SghlColors.humanCareBgGradient),
      child: child,
    );
  }
}
