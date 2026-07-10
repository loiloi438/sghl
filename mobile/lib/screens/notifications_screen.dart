import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../services/notification_inbox_service.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  static const route = '/notifications';

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<NotificationInboxService>().refresh();
    });
  }

  String _formatDate(String iso) {
    try {
      return DateFormat(
        'dd/MM/yyyy HH:mm',
      ).format(DateTime.parse(iso).toLocal());
    } catch (_) {
      return iso;
    }
  }

  @override
  Widget build(BuildContext context) {
    final inbox = context.watch<NotificationInboxService>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Notifications'),
        actions: [
          IconButton(
            onPressed: inbox.loading ? null : () => inbox.refresh(),
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: inbox.loading && inbox.items.isEmpty
          ? const Center(child: CircularProgressIndicator())
          : inbox.items.isEmpty
          ? const Center(
              child: Text(
                'Aucune notification pour le moment.',
                style: TextStyle(color: Colors.grey),
              ),
            )
          : RefreshIndicator(
              onRefresh: inbox.refresh,
              child: ListView.separated(
                padding: const EdgeInsets.all(16),
                itemCount: inbox.items.length,
                separatorBuilder: (_, __) => const SizedBox(height: 8),
                itemBuilder: (context, index) {
                  final n = inbox.items[index];
                  return Material(
                    color: n.lu
                        ? Theme.of(context).cardColor
                        : Theme.of(context).colorScheme.primaryContainer
                              .withValues(alpha: 0.35),
                    borderRadius: BorderRadius.circular(12),
                    child: InkWell(
                      borderRadius: BorderRadius.circular(12),
                      onTap: n.lu ? null : () => inbox.markRead(n.id),
                      child: Padding(
                        padding: const EdgeInsets.all(14),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Expanded(
                                  child: Text(
                                    n.titre,
                                    style: const TextStyle(
                                      fontWeight: FontWeight.w700,
                                      fontSize: 15,
                                    ),
                                  ),
                                ),
                                if (!n.lu)
                                  Container(
                                    width: 8,
                                    height: 8,
                                    decoration: BoxDecoration(
                                      color: Theme.of(
                                        context,
                                      ).colorScheme.primary,
                                      shape: BoxShape.circle,
                                    ),
                                  ),
                              ],
                            ),
                            const SizedBox(height: 6),
                            Text(
                              n.categorie.isEmpty ? 'Information' : n.categorie,
                              style: Theme.of(context).textTheme.labelMedium,
                            ),
                            const SizedBox(height: 6),
                            Text(n.corps),
                            const SizedBox(height: 8),
                            Text(
                              _formatDate(n.createdAt),
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                          ],
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
    );
  }
}
