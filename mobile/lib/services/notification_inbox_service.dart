import 'package:flutter/foundation.dart';

import '../core/api_client.dart';
import '../models/patient_models.dart';

class NotificationInboxService extends ChangeNotifier {
  NotificationInboxService({required ApiClient apiClient}) : _api = apiClient;

  final ApiClient _api;

  List<PatientNotification> _items = [];
  int _unreadCount = 0;
  bool _loading = false;

  List<PatientNotification> get items => _items;
  int get unreadCount => _unreadCount;
  bool get loading => _loading;

  Future<void> refresh() async {
    _loading = true;
    notifyListeners();
    try {
      final listResp = await _api.get('/patient/notifications/');
      final list = _api.decodeList(listResp);
      _items = list
          .map((e) => PatientNotification.fromJson(e as Map<String, dynamic>))
          .toList();

      final countResp = await _api.get('/patient/notifications/non-lues/');
      final countData = _api.decodeMap(countResp);
      _unreadCount = countData['count'] as int? ?? 0;
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  Future<void> markRead(String notificationId) async {
    await _api.post('/patient/notifications/$notificationId/lu/', {});
    await refresh();
  }
}
