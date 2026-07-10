import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ThemeNotifier extends ChangeNotifier {
  static const _key = 'sghl_theme_mode';

  ThemeMode _mode = ThemeMode.light;

  ThemeMode get mode => _mode;

  bool get isDark => _mode == ThemeMode.dark;

  Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    _mode = ThemeMode.light;
    await prefs.setString(_key, 'light');
    notifyListeners();
  }

  Future<void> toggle() async {
    _mode = ThemeMode.light;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_key, 'light');
    notifyListeners();
  }
}
