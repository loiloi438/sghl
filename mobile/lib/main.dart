import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'app.dart';
import 'core/api_client.dart';
import 'core/api_config.dart';
import 'core/theme_notifier.dart';
import 'services/notification_inbox_service.dart';
import 'services/patient_services.dart';
import 'services/staff_services.dart';
import 'services/push_service.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await ApiConfig.init();

  final apiClient = ApiClient();

  runApp(
    MultiProvider(
      providers: [
        Provider<ApiClient>.value(value: apiClient),
        Provider(create: (_) => PushService(apiClient: apiClient)),
        ChangeNotifierProvider(
          create: (ctx) => AuthService(
            apiClient: apiClient,
            pushService: ctx.read<PushService>(),
          ),
        ),
        Provider(create: (_) => PatientService(apiClient: apiClient)),
        Provider(create: (_) => RendezVousStaffService(apiClient: apiClient)),
        ChangeNotifierProvider(
          create: (_) => NotificationInboxService(apiClient: apiClient),
        ),
        ChangeNotifierProvider(create: (_) => ThemeNotifier()),
      ],
      child: const SghlApp(),
    ),
  );
}
