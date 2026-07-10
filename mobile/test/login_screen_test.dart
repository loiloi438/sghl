import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';

import 'package:sghl_mobile/core/sghl_theme.dart';
import 'package:sghl_mobile/core/theme_notifier.dart';
import 'package:sghl_mobile/screens/login_screen.dart';
import 'package:sghl_mobile/services/patient_services.dart';

void main() {
  testWidgets('password visibility toggle changes obscured state', (
    tester,
  ) async {
    final auth = AuthService();
    final themeNotifier = ThemeNotifier();

    await tester.pumpWidget(
      MultiProvider(
        providers: [
          ChangeNotifierProvider<AuthService>.value(value: auth),
          ChangeNotifierProvider<ThemeNotifier>.value(value: themeNotifier),
        ],
        child: MaterialApp(
          theme: SghlTheme.light(),
          home: const LoginScreen(),
        ),
      ),
    );

    final passwordField = find.byType(TextFormField).last;
    expect(passwordField, findsOneWidget);

    await tester.enterText(passwordField, 'secret');
    await tester.pump();

    final toggle = find.byIcon(Icons.visibility_outlined);
    expect(toggle, findsOneWidget);

    await tester.tap(toggle);
    await tester.pump();

    expect(find.byIcon(Icons.visibility_off_outlined), findsOneWidget);
  });
}
