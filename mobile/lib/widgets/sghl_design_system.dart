import 'package:flutter/material.dart';



import '../core/sghl_theme.dart';



/// Espace vertical standard entre sections du tableau de bord.
const double kSectionSpacing = 28;

/// Espace réservé pour la barre de navigation flottante du shell patient.

const double kPatientShellBottomPadding = 100;



/// Carte moderne — `lightSurface` force le blanc sur fond sombre (maquette).

class SghlCard extends StatelessWidget {

  const SghlCard({

    super.key,

    required this.child,

    this.padding = const EdgeInsets.all(18),

    this.onTap,

    this.gradient,

    this.lightSurface = false,

  });



  final Widget child;

  final EdgeInsets padding;

  final VoidCallback? onTap;

  final Gradient? gradient;

  final bool lightSurface;



  @override

  Widget build(BuildContext context) {

    final ext = context.sghl;

    final isDark = Theme.of(context).brightness == Brightness.dark;

    final bgColor = gradient == null

        ? (lightSurface || isDark

            ? ext.contentCardColor

            : Theme.of(context).cardTheme.color)

        : null;



    final content = Container(

      width: double.infinity,

      padding: padding,

      decoration: BoxDecoration(

        gradient: gradient,

        color: bgColor,

        borderRadius: BorderRadius.circular(26),

        boxShadow: ext.cardShadow,

        border: Border.all(

          color: (lightSurface || isDark)

              ? Colors.black.withValues(alpha: 0.04)

              : Theme.of(context).colorScheme.outline.withValues(alpha: 0.2),

        ),

      ),

      child: DefaultTextStyle.merge(
        style: SghlTypography.montserrat(
          fontSize: SghlTypography.body,
          fontWeight: FontWeight.w500,
          color: (lightSurface || isDark)
              ? ext.textOnCard
              : Theme.of(context).colorScheme.onSurface,
        ),
        child: IconTheme.merge(
          data: IconThemeData(
            color: (lightSurface || isDark)
                ? ext.textOnCard
                : Theme.of(context).colorScheme.onSurface,
          ),

          child: child,

        ),

      ),

    );



    if (onTap == null) return content;

    return Material(

      color: Colors.transparent,

      child: InkWell(

        onTap: onTap,

        borderRadius: BorderRadius.circular(26),

        child: content,

      ),

    );

  }

}



enum SghlFeedbackType { error, success, info, warning }



/// Bannière d'erreur style maquette (fond corail doux).

class SghlFeedbackBanner extends StatelessWidget {

  const SghlFeedbackBanner({

    super.key,

    required this.message,

    required this.type,

    this.onDismiss,
    this.compact = false,
    this.title,
  });

  final String message;
  final SghlFeedbackType type;
  final VoidCallback? onDismiss;
  final bool compact;
  final String? title;



  @override

  Widget build(BuildContext context) {

    final (icon, bg, fg, defaultTitle) = switch (type) {
      SghlFeedbackType.error => (
          Icons.health_and_safety_outlined,
          const Color(0xFFFFE8E5),
          const Color(0xFFE57373),
          'Connexion interrompue',
        ),

      SghlFeedbackType.success => (

          Icons.check_circle_outline_rounded,

          SghlColors.mintGreen.withValues(alpha: 0.25),

          const Color(0xFF1B7A52),

          'C\'est bon',

        ),

      SghlFeedbackType.info => (

          Icons.info_outline_rounded,

          SghlColors.medicalBlue.withValues(alpha: 0.12),

          SghlColors.medicalBlue,

          'Information',

        ),

      SghlFeedbackType.warning => (

          Icons.warning_amber_rounded,

          const Color(0xFFFFF3CD),

          const Color(0xFFB45309),

          'Attention',

        ),

    };

    final displayTitle = title ?? defaultTitle;

    return Container(

      width: double.infinity,

      padding: EdgeInsets.all(compact ? 12 : 16),

      decoration: BoxDecoration(

        color: bg,

        borderRadius: BorderRadius.circular(18),

        boxShadow: context.sghl.cardShadow,

      ),

      child: Row(

        crossAxisAlignment: CrossAxisAlignment.start,

        children: [

          Container(

            padding: const EdgeInsets.all(8),

            decoration: BoxDecoration(

              color: fg.withValues(alpha: 0.15),

              shape: BoxShape.circle,

            ),

            child: Icon(icon, color: fg, size: 22),

          ),

          const SizedBox(width: 12),

          Expanded(

            child: Column(

              crossAxisAlignment: CrossAxisAlignment.start,

              children: [

                Text(
                  displayTitle,

                  style: Theme.of(context).textTheme.labelLarge?.copyWith(

                        color: fg,

                        fontWeight: FontWeight.w800,

                      ),

                ),

                const SizedBox(height: 4),

                Text(
                  message,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: SghlColors.textLight,
                        fontWeight: FontWeight.w500,
                      ),
                ),

              ],

            ),

          ),

          if (onDismiss != null)

            IconButton(

              onPressed: onDismiss,

              icon: const Icon(Icons.close, size: 18),

              visualDensity: VisualDensity.compact,

            ),

        ],

      ),

    );

  }

}



/// Fond dégradé connexion (bleu clair → blanc).

class SghlLoginBackground extends StatelessWidget {

  const SghlLoginBackground({super.key, required this.child});



  final Widget child;



  @override

  Widget build(BuildContext context) {

    return Container(

      decoration: const BoxDecoration(gradient: SghlColors.loginGradient),

      child: Stack(

        children: [

          Positioned(

            top: -40,

            right: -30,

            child: Container(

              width: 180,

              height: 180,

              decoration: BoxDecoration(

                shape: BoxShape.circle,

                color: SghlColors.medicalBlue.withValues(alpha: 0.08),

              ),

            ),

          ),

          Positioned(

            bottom: 80,

            left: -50,

            child: Container(

              width: 140,

              height: 140,

              decoration: BoxDecoration(

                shape: BoxShape.circle,

                color: SghlColors.turquoise.withValues(alpha: 0.1),

              ),

            ),

          ),

          child,

        ],

      ),

    );

  }

}



/// En-tête maquette : salutation à gauche, avatar à droite.

class SghlDashboardHero extends StatelessWidget {

  const SghlDashboardHero({

    super.key,

    required this.prenom,

    this.trailing,

  });



  final String prenom;

  final Widget? trailing;



  @override

  Widget build(BuildContext context) {

    final initial = prenom.isNotEmpty ? prenom[0].toUpperCase() : '?';

    final greeting = prenom.isNotEmpty ? 'Bonjour $prenom 👋' : 'Bonjour 👋';



    return Padding(

      padding: const EdgeInsets.fromLTRB(20, 52, 20, 8),

      child: Row(

        children: [

          Expanded(

            child: Text(
              greeting,
              style: SghlTypography.montserrat(
                fontSize: SghlTypography.headline,
                fontWeight: FontWeight.w700,
                color: Theme.of(context).colorScheme.onSurface,
              ),
            ),

          ),

          if (trailing != null) trailing!,

          const SizedBox(width: 8),

          Container(

            padding: const EdgeInsets.all(3),

            decoration: BoxDecoration(

              shape: BoxShape.circle,

              border: Border.all(

                color: SghlColors.turquoise.withValues(alpha: 0.6),

                width: 2,

              ),

            ),

            child: CircleAvatar(

              radius: 26,

              backgroundColor: SghlColors.medicalBlue.withValues(alpha: 0.2),

              foregroundColor: Colors.white,

              child: Text(
                initial,
                style: SghlTypography.montserrat(
                  fontSize: 22,
                  fontWeight: FontWeight.w800,
                  color: Colors.white,
                ),
              ),

            ),

          ),

        ],

      ),

    );

  }

}



/// Petite carte statistique (3 en ligne sur le tableau de bord).

class SghlStatCard extends StatelessWidget {
  const SghlStatCard({
    super.key,
    required this.value,
    required this.label,
    this.icon,
    this.accent,
    this.backgroundColor,
  });

  final String value;
  final String label;
  final IconData? icon;
  final Color? accent;
  final Color? backgroundColor;

  @override
  Widget build(BuildContext context) {
    final bg = backgroundColor ?? const Color(0xFF2A4A6B);
    final accentColor = accent ?? Colors.white;

    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 14),
        decoration: BoxDecoration(
          color: bg,
          borderRadius: BorderRadius.circular(22),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.2),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (icon != null) Icon(icon, size: 18, color: accentColor),
            if (icon != null) const SizedBox(height: 6),
            Text(
              value,
              style: SghlTypography.montserrat(
                fontSize: 22,
                fontWeight: FontWeight.w800,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 2),
            Text(
              label,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: SghlTypography.montserrat(
                fontSize: 11,
                fontWeight: FontWeight.w500,
                color: Colors.white.withValues(alpha: 0.9),
                height: 1.2,
              ),
            ),
          ],
        ),
      ),
    );
  }
}



/// Tuile raccourci grille 2 colonnes.

class SghlShortcutTile extends StatelessWidget {

  const SghlShortcutTile({

    super.key,

    required this.icon,

    required this.label,

    required this.color,

    required this.onTap,

  });



  final IconData icon;

  final String label;

  final Color color;

  final VoidCallback onTap;



  @override

  Widget build(BuildContext context) {

    return SghlCard(

      lightSurface: true,

      padding: const EdgeInsets.symmetric(vertical: 18, horizontal: 12),

      onTap: onTap,

      child: Column(

        mainAxisAlignment: MainAxisAlignment.center,

        children: [

          Container(

            padding: const EdgeInsets.all(10),

            decoration: BoxDecoration(

              color: color.withValues(alpha: 0.15),

              borderRadius: BorderRadius.circular(14),

            ),

            child: Icon(icon, color: color, size: 26),

          ),

          const SizedBox(height: 10),

          Text(
            label,
            textAlign: TextAlign.center,
            style: SghlTypography.montserrat(
              fontWeight: FontWeight.w600,
              fontSize: 14,
              color: SghlColors.textLight,
            ),
          ),

        ],

      ),

    );

  }

}



class SghlNavItem {

  const SghlNavItem({

    required this.icon,

    required this.selectedIcon,

    this.label,

  });



  final IconData icon;

  final IconData selectedIcon;

  final String? label;

}



/// Barre flottante icônes seules (maquette).

class SghlFloatingNavBar extends StatelessWidget {

  const SghlFloatingNavBar({

    super.key,

    required this.items,

    required this.selectedIndex,

    required this.onSelected,

    this.badges = const {},
    this.compact = true,
    this.lightBar = true,
  });

  final List<SghlNavItem> items;
  final int selectedIndex;
  final ValueChanged<int> onSelected;
  final Map<int, int> badges;
  final bool compact;
  /// Barre blanche (accueil) ou sombre (écran RDV) comme sur la maquette.
  final bool lightBar;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 28),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
      decoration: BoxDecoration(
        color: lightBar ? Colors.white : const Color(0xFF2A3348),

        borderRadius: BorderRadius.circular(32),

        boxShadow: [

          BoxShadow(

            color: Colors.black.withValues(alpha: lightBar ? 0.14 : 0.45),

            blurRadius: 28,

            offset: const Offset(0, 10),

          ),

        ],

      ),

      child: Row(

        mainAxisAlignment: MainAxisAlignment.spaceAround,

        children: List.generate(items.length, (i) {

          final item = items[i];

          final selected = i == selectedIndex;

          final badge = badges[i] ?? 0;



          return InkWell(

            onTap: () => onSelected(i),

            borderRadius: BorderRadius.circular(26),

            child: AnimatedContainer(

              duration: const Duration(milliseconds: 220),

              padding: const EdgeInsets.all(10),

              decoration: BoxDecoration(

                color: selected
                    ? (lightBar
                        ? SghlColors.humanCareTeal.withValues(alpha: 0.12)
                        : Colors.white.withValues(alpha: 0.12))
                    : Colors.transparent,

                borderRadius: BorderRadius.circular(16),

              ),

              child: Badge(

                isLabelVisible: badge > 0,

                label: Text(badge > 9 ? '9+' : '$badge'),

                backgroundColor: SghlColors.coral,

                child: Icon(

                  selected ? item.selectedIcon : item.icon,

                  color: lightBar
                      ? (selected
                          ? SghlColors.humanCareTeal
                          : SghlColors.humanCareMuted)
                      : (selected
                          ? Colors.white
                          : SghlColors.mutedDark),

                  size: 26,

                ),

              ),

            ),

          );

        }),

      ),

    );

  }

}



/// Bouton dégradé corail → orange (Réessayer, Prendre RDV).

class SghlGradientButton extends StatelessWidget {

  const SghlGradientButton({

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

        gradient: SghlColors.ctaGradient,

        borderRadius: BorderRadius.circular(compact ? 28 : 16),

        boxShadow: [

          BoxShadow(

            color: SghlColors.coral.withValues(alpha: 0.35),

            blurRadius: 12,

            offset: const Offset(0, 4),

          ),

        ],

      ),

      child: Material(

        color: Colors.transparent,

        child: InkWell(
          onTap: loading ? null : onPressed,
          borderRadius: BorderRadius.circular(compact ? 28 : 16),
          splashColor: Colors.white.withValues(alpha: 0.25),
          highlightColor: Colors.white.withValues(alpha: 0.12),

          child: Container(

            width: compact ? null : double.infinity,

            padding: EdgeInsets.symmetric(

              horizontal: compact ? 22 : 24,

              vertical: compact ? 14 : 16,

            ),

            alignment: compact ? null : Alignment.center,

            child: loading

                ? const SizedBox(

                    height: 22,

                    width: 22,

                    child: CircularProgressIndicator(

                      strokeWidth: 2,

                      color: Colors.white,

                    ),

                  )

                : Row(

                    mainAxisSize: compact ? MainAxisSize.min : MainAxisSize.max,

                    mainAxisAlignment: MainAxisAlignment.center,

                    children: [

                      if (icon != null) ...[

                        Icon(icon, color: Colors.white, size: 20),

                        const SizedBox(width: 8),

                      ],

                      Text(
                        label,
                        style: SghlTypography.montserrat(
                          color: Colors.white,
                          fontWeight: FontWeight.w600,
                          fontSize: SghlTypography.body,
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



/// Bouton primaire bleu marine (connexion).

class SghlPrimaryButton extends StatelessWidget {

  const SghlPrimaryButton({

    super.key,

    required this.label,

    required this.onPressed,

    this.loading = false,

  });



  final String label;

  final VoidCallback? onPressed;

  final bool loading;



  @override

  Widget build(BuildContext context) {

    return FilledButton(

      onPressed: loading ? null : onPressed,

      style: FilledButton.styleFrom(

        backgroundColor: SghlColors.medicalBlueDark,

        foregroundColor: Colors.white,

        minimumSize: const Size(double.infinity, 52),

        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),

        elevation: 2,
      ),

      child: loading

          ? const SizedBox(

              height: 22,

              width: 22,

              child: CircularProgressIndicator(

                strokeWidth: 2,

                color: Colors.white,

              ),

            )

          : Text(label),

    );

  }

}



/// Illustration vide état médical (icônes empilées).

class SghlMedicalEmptyIllustration extends StatelessWidget {

  const SghlMedicalEmptyIllustration({super.key});



  @override

  Widget build(BuildContext context) {

    return SizedBox(

      height: 160,

      child: Stack(

        alignment: Alignment.center,

        children: [

          _bubble(Icons.medication_liquid_outlined, 48, -70, 0,

              SghlColors.medicalBlue),

          _bubble(Icons.assignment_outlined, 56, 60, -20, SghlColors.coral),

          _bubble(Icons.calendar_month_rounded, 52, -10, 30,

              SghlColors.gold),

        ],

      ),

    );

  }



  Widget _bubble(IconData icon, double size, double dx, double dy, Color color) {

    return Transform.translate(

      offset: Offset(dx, dy),

      child: Container(

        width: size + 24,

        height: size + 24,

        decoration: BoxDecoration(

          color: color.withValues(alpha: 0.15),

          borderRadius: BorderRadius.circular(18),

          boxShadow: [

            BoxShadow(

              color: color.withValues(alpha: 0.2),

              blurRadius: 16,

              offset: const Offset(0, 6),

            ),

          ],

        ),

        child: Icon(icon, color: color, size: size * 0.55),

      ),

    );

  }

}



/// État vide humanisé avec icône médicale.
class SghlEmptyState extends StatelessWidget {
  const SghlEmptyState({
    super.key,
    required this.message,
    this.icon = Icons.medical_services_outlined,
    this.subtitle,
  });

  final String message;
  final IconData icon;
  final String? subtitle;

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 20),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: SghlColors.medicalBlue.withValues(alpha: isDark ? 0.2 : 0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, size: 40, color: SghlColors.medicalBlue),
          ),
          const SizedBox(height: 16),
          Text(
            message,
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w600,
                  fontSize: 17,
                ),
          ),
          if (subtitle != null) ...[
            const SizedBox(height: 8),
            Text(
              subtitle!,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w400,
                    color: Theme.of(context).colorScheme.onSurface.withValues(
                          alpha: 0.72,
                        ),
                  ),
            ),
          ],
        ],
      ),
    );
  }
}



/// Titre de section avec séparateur.

class SghlSectionHeader extends StatelessWidget {

  const SghlSectionHeader({super.key, required this.title});



  final String title;



  @override

  Widget build(BuildContext context) {

    return Column(

      crossAxisAlignment: CrossAxisAlignment.start,

      children: [

        Text(
          title,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w700,
                fontSize: SghlTypography.title,
              ),
        ),

        const SizedBox(height: 12),

        Divider(
          color: Theme.of(context).colorScheme.outline.withValues(alpha: 0.35),
          height: 1,
        ),
        const SizedBox(height: 4),

      ],

    );

  }

}



// Alias rétrocompatibilité

typedef SghlCoralButton = SghlGradientButton;


