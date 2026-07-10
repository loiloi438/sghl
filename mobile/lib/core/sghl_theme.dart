import 'package:flutter/material.dart';

/// Palette alignée sur l'interface web staff SGHL.
abstract final class SghlColors {
  static const primary = Color(0xFF2563EB);
  static const primaryDark = Color(0xFF1D4ED8);
  static const accent = Color(0xFF059669);
  static const bg = Color(0xFFF4F7FB);
  static const surface = Color(0xFFFFFFFF);
  static const border = Color(0xFFE2E8F0);
  static const text = Color(0xFF0F172A);
  static const muted = Color(0xFF64748B);

  // Mode sombre adouci : fond clair harmonisé (aligné web)
  static const bgDark = Color(0xFFF4F7FB);
  static const surfaceDark = Color(0xFFFFFFFF);
  static const borderDark = Color(0xFFE2E8F0);
  static const textDark = Color(0xFF0F172A);
}

abstract final class SghlTheme {
  static ThemeData light() {
    final scheme = ColorScheme.fromSeed(
      seedColor: SghlColors.primary,
      primary: SghlColors.primary,
      secondary: SghlColors.accent,
      surface: SghlColors.surface,
      brightness: Brightness.light,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      scaffoldBackgroundColor: SghlColors.bg,
      appBarTheme: const AppBarTheme(
        centerTitle: true,
        elevation: 0,
        scrolledUnderElevation: 2,
        backgroundColor: SghlColors.surface,
        foregroundColor: SghlColors.text,
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(14),
          side: const BorderSide(color: SghlColors.border),
        ),
        color: SghlColors.surface,
        margin: EdgeInsets.zero,
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: SghlColors.primary,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          elevation: 0,
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: SghlColors.surface,
        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
        labelStyle: const TextStyle(fontWeight: FontWeight.w600, color: Color(0xFF475569)),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: SghlColors.border),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: SghlColors.border),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: Color(0xFF60A5FA), width: 1.5),
        ),
      ),
      chipTheme: ChipThemeData(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        side: const BorderSide(color: SghlColors.border),
        backgroundColor: SghlColors.surface,
        labelStyle: const TextStyle(fontWeight: FontWeight.w600),
      ),
    );
  }

  /// Conservé pour compatibilité : même rendu que le thème clair.
  static ThemeData dark() => light();
}
