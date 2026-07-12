import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Palette SGHL alignée sur la maquette visuelle.
abstract final class SghlColors {
  static const medicalBlue = Color(0xFF1A7FBF);
  static const navy = Color(0xFF1A233A);
  static const navyDeep = Color(0xFF0D1B2A);
  static const medicalBlueDark = Color(0xFF1E3A5F);
  static const turquoise = Color(0xFF2EC4B6);
  static const mintGreen = Color(0xFF5CB88A);
  static const coral = Color(0xFFFF6F61);
  static const coralSoft = Color(0xFFFFE8E5);
  static const gold = Color(0xFFFFB347);
  static const statusGreen = Color(0xFF4CAF50);

  static const bgLight = Color(0xFFE8F4FC);
  static const bgLightSoft = Color(0xFFF5FAFF);
  static const surfaceLight = Color(0xFFFFFFFF);

  /// Texte principal sur fond clair — contraste élevé.
  static const textLight = Color(0xFF333333);
  static const mutedLight = Color(0xFF666666);
  static const subtleLight = Color(0xFF888888);

  static const bgDark = Color(0xFF1A2533);
  static const surfaceDark = Color(0xFF252D45);

  /// Texte sur fond bleu nuit — blanc pur.
  static const textDark = Color(0xFFFFFFFF);
  static const mutedDark = Color(0xFFD0D4DC);
  static const subtleDark = Color(0xFFB0B6C2);

  static const borderDark = Color(0xFF3D4660);

  static const primaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [medicalBlue, turquoise],
  );

  static const heroGradientLight = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFFD6ECFA), Color(0xFFF5FAFF)],
  );

  static const heroGradientDark = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFF1A233A), Color(0xFF0D1B2A)],
  );

  static const ctaGradient = LinearGradient(
    begin: Alignment.centerLeft,
    end: Alignment.centerRight,
    colors: [Color(0xFFFFB347), Color(0xFFFF6F61)],
  );

  static const loginGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [Color(0xFFD4E9F7), Color(0xFFF8FBFF)],
  );

  // Human-Care — portail patient (pastels)
  static const humanCareBg = Color(0xFFF0FDF9);
  static const humanCareMint = Color(0xFF6EE7B7);
  static const humanCareMintDark = Color(0xFF34D399);
  static const humanCareTeal = Color(0xFF0D9488);
  static const humanCareText = Color(0xFF134E4A);
  static const humanCareMuted = Color(0xFF64748B);
  static const humanCareSky = Color(0xFFE0F2FE);
  static const humanCareSand = Color(0xFFFEF3C7);
  static const humanCareLavender = Color(0xFFEDE9FE);

  static const humanCareBgGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFFF0FDF9), Color(0xFFE0F2FE)],
  );

  static const humanCareCtaGradient = LinearGradient(
    begin: Alignment.centerLeft,
    end: Alignment.centerRight,
    colors: [Color(0xFF6EE7B7), Color(0xFF34D399)],
  );
}

/// Échelle typographique SGHL — Montserrat, lisibilité premium.
abstract final class SghlTypography {
  static const double letterSpacing = 0.5;
  static const double body = 16;
  static const double bodyLarge = 17;
  static const double label = 14;
  static const double title = 20;
  static const double headline = 24;
  static const double display = 28;

  static TextStyle montserrat({
    required double fontSize,
    required FontWeight fontWeight,
    required Color color,
    double? height,
    double? letterSpacing,
  }) {
    return GoogleFonts.montserrat(
      fontSize: fontSize,
      fontWeight: fontWeight,
      color: color,
      height: height ?? 1.45,
      letterSpacing: letterSpacing ?? SghlTypography.letterSpacing,
    );
  }

  static TextStyle nunito({
    required double fontSize,
    required FontWeight fontWeight,
    required Color color,
    double? height,
  }) {
    return GoogleFonts.nunito(
      fontSize: fontSize,
      fontWeight: fontWeight,
      color: color,
      height: height ?? 1.45,
    );
  }

  static TextStyle poppins({
    required double fontSize,
    required FontWeight fontWeight,
    required Color color,
    double? height,
  }) {
    return GoogleFonts.poppins(
      fontSize: fontSize,
      fontWeight: fontWeight,
      color: color,
      height: height ?? 1.35,
    );
  }
}

class SghlThemeExtension extends ThemeExtension<SghlThemeExtension> {
  const SghlThemeExtension({
    required this.primaryGradient,
    required this.cardShadow,
    required this.coral,
    required this.mint,
    required this.contentCardColor,
    required this.textOnCard,
    required this.mutedOnCard,
  });

  final Gradient primaryGradient;
  final List<BoxShadow> cardShadow;
  final Color coral;
  final Color mint;
  final Color contentCardColor;
  final Color textOnCard;
  final Color mutedOnCard;

  @override
  SghlThemeExtension copyWith({
    Gradient? primaryGradient,
    List<BoxShadow>? cardShadow,
    Color? coral,
    Color? mint,
    Color? contentCardColor,
    Color? textOnCard,
    Color? mutedOnCard,
  }) {
    return SghlThemeExtension(
      primaryGradient: primaryGradient ?? this.primaryGradient,
      cardShadow: cardShadow ?? this.cardShadow,
      coral: coral ?? this.coral,
      mint: mint ?? this.mint,
      contentCardColor: contentCardColor ?? this.contentCardColor,
      textOnCard: textOnCard ?? this.textOnCard,
      mutedOnCard: mutedOnCard ?? this.mutedOnCard,
    );
  }

  @override
  SghlThemeExtension lerp(SghlThemeExtension? other, double t) => this;
}

extension SghlThemeContext on BuildContext {
  static const _fallback = SghlThemeExtension(
    primaryGradient: SghlColors.heroGradientLight,
    cardShadow: [],
    coral: SghlColors.coral,
    mint: SghlColors.mintGreen,
    contentCardColor: SghlColors.surfaceLight,
    textOnCard: SghlColors.textLight,
    mutedOnCard: SghlColors.mutedLight,
  );

  SghlThemeExtension get sghl =>
      Theme.of(this).extension<SghlThemeExtension>() ?? _fallback;
}

abstract final class SghlTheme {
  static TextTheme _textTheme({
    required Color primary,
    required Color secondary,
    required Color subtle,
  }) {
    return TextTheme(
      displaySmall: SghlTypography.montserrat(
        fontSize: SghlTypography.display,
        fontWeight: FontWeight.w800,
        color: primary,
      ),
      headlineSmall: SghlTypography.montserrat(
        fontSize: SghlTypography.headline,
        fontWeight: FontWeight.w700,
        color: primary,
      ),
      titleLarge: SghlTypography.montserrat(
        fontSize: SghlTypography.title,
        fontWeight: FontWeight.w700,
        color: primary,
      ),
      titleMedium: SghlTypography.montserrat(
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: primary,
      ),
      titleSmall: SghlTypography.montserrat(
        fontSize: SghlTypography.label,
        fontWeight: FontWeight.w600,
        color: primary,
      ),
      bodyLarge: SghlTypography.montserrat(
        fontSize: SghlTypography.bodyLarge,
        fontWeight: FontWeight.w500,
        color: primary,
      ),
      bodyMedium: SghlTypography.montserrat(
        fontSize: SghlTypography.body,
        fontWeight: FontWeight.w500,
        color: secondary,
      ),
      bodySmall: SghlTypography.montserrat(
        fontSize: SghlTypography.label,
        fontWeight: FontWeight.w400,
        color: subtle,
      ),
      labelLarge: SghlTypography.montserrat(
        fontSize: SghlTypography.label,
        fontWeight: FontWeight.w600,
        color: primary,
      ),
      labelMedium: SghlTypography.montserrat(
        fontSize: 13,
        fontWeight: FontWeight.w500,
        color: secondary,
      ),
      labelSmall: SghlTypography.montserrat(
        fontSize: 12,
        fontWeight: FontWeight.w500,
        color: subtle,
      ),
    );
  }

  static List<BoxShadow> _cardShadow(bool dark) => [
        BoxShadow(
          color: Colors.black.withValues(alpha: dark ? 0.28 : 0.08),
          blurRadius: 20,
          offset: const Offset(0, 8),
        ),
      ];

  static TextStyle _buttonText(Color color) => SghlTypography.montserrat(
        fontSize: SghlTypography.body,
        fontWeight: FontWeight.w600,
        color: color,
        letterSpacing: 0.4,
      );

  static ThemeData light() {
    const ext = SghlThemeExtension(
      primaryGradient: SghlColors.loginGradient,
      cardShadow: [],
      coral: SghlColors.coral,
      mint: SghlColors.mintGreen,
      contentCardColor: SghlColors.surfaceLight,
      textOnCard: SghlColors.textLight,
      mutedOnCard: SghlColors.mutedLight,
    );

    final textTheme = _textTheme(
      primary: SghlColors.textLight,
      secondary: SghlColors.mutedLight,
      subtle: SghlColors.subtleLight,
    );

    final scheme = ColorScheme.light(
      primary: SghlColors.medicalBlueDark,
      onPrimary: Colors.white,
      secondary: SghlColors.mintGreen,
      onSecondary: SghlColors.textLight,
      tertiary: SghlColors.coral,
      surface: SghlColors.surfaceLight,
      onSurface: SghlColors.textLight,
      error: SghlColors.coral,
      onError: Colors.white,
      outline: const Color(0xFFD8E4EE),
    );

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      colorScheme: scheme,
      scaffoldBackgroundColor: SghlColors.bgLightSoft,
      fontFamily: GoogleFonts.montserrat().fontFamily,
      textTheme: textTheme,
      primaryTextTheme: textTheme,
      extensions: [ext.copyWith(cardShadow: _cardShadow(false))],
      appBarTheme: AppBarTheme(
        centerTitle: true,
        elevation: 0,
        scrolledUnderElevation: 0,
        backgroundColor: Colors.transparent,
        foregroundColor: SghlColors.textLight,
        titleTextStyle: textTheme.titleLarge,
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        color: SghlColors.surfaceLight,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        margin: EdgeInsets.zero,
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: SghlColors.medicalBlueDark,
          foregroundColor: Colors.white,
          textStyle: _buttonText(Colors.white),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(28),
          ),
          elevation: 2,
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: SghlColors.medicalBlueDark,
          backgroundColor: Colors.white,
          textStyle: _buttonText(SghlColors.medicalBlueDark),
          side: const BorderSide(color: SghlColors.medicalBlueDark, width: 1.5),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(28),
          ),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: SghlColors.medicalBlueDark,
          textStyle: _buttonText(SghlColors.medicalBlueDark),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: SghlColors.surfaceLight,
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
        labelStyle: SghlTypography.montserrat(
          fontSize: SghlTypography.label,
          fontWeight: FontWeight.w600,
          color: SghlColors.mutedLight,
        ),
        hintStyle: SghlTypography.montserrat(
          fontSize: SghlTypography.body,
          fontWeight: FontWeight.w400,
          color: SghlColors.subtleLight,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(28),
          borderSide: const BorderSide(color: Color(0xFFD8E4EE)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(28),
          borderSide: const BorderSide(color: Color(0xFFD8E4EE)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(28),
          borderSide:
              const BorderSide(color: SghlColors.medicalBlue, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(28),
          borderSide: const BorderSide(color: SghlColors.coral),
        ),
      ),
    );
  }

  static ThemeData dark() {
    const ext = SghlThemeExtension(
      primaryGradient: SghlColors.heroGradientDark,
      cardShadow: [],
      coral: SghlColors.coral,
      mint: SghlColors.mintGreen,
      contentCardColor: SghlColors.surfaceLight,
      textOnCard: SghlColors.textLight,
      mutedOnCard: SghlColors.mutedLight,
    );

    final textTheme = _textTheme(
      primary: SghlColors.textDark,
      secondary: SghlColors.mutedDark,
      subtle: SghlColors.subtleDark,
    );

    final scheme = ColorScheme.dark(
      primary: SghlColors.turquoise,
      onPrimary: SghlColors.bgDark,
      secondary: SghlColors.mintGreen,
      onSecondary: SghlColors.bgDark,
      tertiary: SghlColors.coral,
      surface: SghlColors.surfaceDark,
      onSurface: SghlColors.textDark,
      error: SghlColors.coral,
      onError: Colors.white,
      outline: SghlColors.borderDark,
    );

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: scheme,
      scaffoldBackgroundColor: SghlColors.bgDark,
      fontFamily: GoogleFonts.montserrat().fontFamily,
      textTheme: textTheme,
      primaryTextTheme: textTheme,
      extensions: [ext.copyWith(cardShadow: _cardShadow(true))],
      appBarTheme: AppBarTheme(
        centerTitle: false,
        elevation: 0,
        backgroundColor: Colors.transparent,
        foregroundColor: SghlColors.textDark,
        titleTextStyle: textTheme.titleLarge,
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        color: SghlColors.surfaceLight,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        margin: EdgeInsets.zero,
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: SghlColors.turquoise,
          foregroundColor: SghlColors.bgDark,
          textStyle: _buttonText(SghlColors.bgDark),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(28),
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: SghlColors.turquoise,
          textStyle: _buttonText(SghlColors.turquoise),
          side: const BorderSide(color: SghlColors.turquoise),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(28),
          ),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: SghlColors.turquoise,
          textStyle: _buttonText(SghlColors.turquoise),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: SghlColors.surfaceDark,
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
        labelStyle: SghlTypography.montserrat(
          fontSize: SghlTypography.label,
          fontWeight: FontWeight.w600,
          color: SghlColors.mutedDark,
        ),
        hintStyle: SghlTypography.montserrat(
          fontSize: SghlTypography.body,
          fontWeight: FontWeight.w400,
          color: SghlColors.subtleDark,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(28),
          borderSide: const BorderSide(color: SghlColors.borderDark),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(28),
          borderSide: const BorderSide(color: SghlColors.borderDark),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(28),
          borderSide: const BorderSide(color: SghlColors.turquoise, width: 2),
        ),
      ),
    );
  }

  /// Thème Human-Care — portail patient (clair, pastels, Nunito/Poppins).
  static ThemeData patientHumanCare() {
    const ext = SghlThemeExtension(
      primaryGradient: SghlColors.humanCareBgGradient,
      cardShadow: [],
      coral: SghlColors.coral,
      mint: SghlColors.humanCareMintDark,
      contentCardColor: Colors.white,
      textOnCard: SghlColors.humanCareText,
      mutedOnCard: SghlColors.humanCareMuted,
    );

    final textTheme = TextTheme(
      displaySmall: SghlTypography.poppins(
        fontSize: SghlTypography.display,
        fontWeight: FontWeight.w800,
        color: SghlColors.humanCareText,
      ),
      headlineSmall: SghlTypography.poppins(
        fontSize: SghlTypography.headline,
        fontWeight: FontWeight.w700,
        color: SghlColors.humanCareText,
      ),
      titleLarge: SghlTypography.poppins(
        fontSize: SghlTypography.title,
        fontWeight: FontWeight.w700,
        color: SghlColors.humanCareText,
      ),
      titleMedium: SghlTypography.poppins(
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: SghlColors.humanCareText,
      ),
      titleSmall: SghlTypography.nunito(
        fontSize: SghlTypography.label,
        fontWeight: FontWeight.w700,
        color: SghlColors.humanCareText,
      ),
      bodyLarge: SghlTypography.nunito(
        fontSize: SghlTypography.bodyLarge,
        fontWeight: FontWeight.w600,
        color: SghlColors.humanCareText,
      ),
      bodyMedium: SghlTypography.nunito(
        fontSize: SghlTypography.body,
        fontWeight: FontWeight.w500,
        color: SghlColors.humanCareMuted,
      ),
      bodySmall: SghlTypography.nunito(
        fontSize: SghlTypography.label,
        fontWeight: FontWeight.w500,
        color: SghlColors.humanCareMuted,
      ),
      labelLarge: SghlTypography.nunito(
        fontSize: SghlTypography.label,
        fontWeight: FontWeight.w700,
        color: SghlColors.humanCareTeal,
      ),
    );

    final scheme = ColorScheme.light(
      primary: SghlColors.humanCareTeal,
      onPrimary: Colors.white,
      secondary: SghlColors.humanCareMintDark,
      onSecondary: SghlColors.humanCareText,
      tertiary: SghlColors.coral,
      surface: Colors.white,
      onSurface: SghlColors.humanCareText,
      error: SghlColors.coral,
      onError: Colors.white,
      outline: const Color(0xFF99F6E4),
    );

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      colorScheme: scheme,
      scaffoldBackgroundColor: SghlColors.humanCareBg,
      fontFamily: GoogleFonts.nunito().fontFamily,
      textTheme: textTheme,
      primaryTextTheme: textTheme,
      extensions: [ext.copyWith(cardShadow: _cardShadow(false))],
      appBarTheme: AppBarTheme(
        centerTitle: true,
        elevation: 0,
        scrolledUnderElevation: 0,
        backgroundColor: Colors.transparent,
        foregroundColor: SghlColors.humanCareText,
        titleTextStyle: textTheme.titleLarge,
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        color: Colors.white,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        margin: EdgeInsets.zero,
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: SghlColors.humanCareMintDark,
          foregroundColor: const Color(0xFF064E3B),
          textStyle: SghlTypography.poppins(
            fontSize: SghlTypography.body,
            fontWeight: FontWeight.w700,
            color: const Color(0xFF064E3B),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(999),
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: SghlColors.humanCareTeal,
          backgroundColor: Colors.white,
          side: const BorderSide(color: Color(0xFFA7F3D0)),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(999),
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: const Color(0xFFECFDF5),
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(20),
          borderSide: const BorderSide(color: Color(0xFFA7F3D0)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(20),
          borderSide: const BorderSide(color: Color(0xFFA7F3D0)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(20),
          borderSide: const BorderSide(color: SghlColors.humanCareTeal, width: 2),
        ),
      ),
    );
  }
}
