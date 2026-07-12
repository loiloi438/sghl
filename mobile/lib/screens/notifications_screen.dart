import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../core/sghl_theme.dart';
import '../services/notification_inbox_service.dart';
import '../widgets/human_care_widgets.dart';
import '../widgets/patient_human_care_page.dart';
import '../widgets/sghl_design_system.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key, this.embedded = false});

  static const route = '/notifications';

  final bool embedded;

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
      return DateFormat('dd/MM/yyyy HH:mm').format(DateTime.parse(iso).toLocal());
    } catch (_) {
      return iso;
    }
  }

  Widget _header(NotificationInboxService inbox) {
    return PatientHcHeader(
      title: 'Notifications',
      subtitle: 'Rappels, confirmations et messages de l\'hôpital',
      embedded: widget.embedded,
      actions: [
        IconButton(
          onPressed: inbox.loading ? null : inbox.refresh,
          icon: const Icon(Icons.refresh_rounded),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final inbox = context.watch<NotificationInboxService>();
    final bottomPad = widget.embedded ? kPatientShellBottomPadding : 16.0;
    final topPad = widget.embedded ? 8.0 : 16.0;

    return Scaffold(
      appBar: widget.embedded
          ? null
          : AppBar(
              title: const Text('Notifications'),
              actions: [
                IconButton(
                  onPressed: inbox.loading ? null : inbox.refresh,
                  icon: const Icon(Icons.refresh_rounded),
                ),
              ],
            ),
      body: SghlHumanCareBackground(
        child: inbox.loading && inbox.items.isEmpty
            ? const Center(child: CircularProgressIndicator())
            : inbox.items.isEmpty
                ? ListView(
                    padding: EdgeInsets.fromLTRB(16, topPad, 16, bottomPad),
                    children: [
                      _header(inbox),
                      const SghlEmptyState(
                        icon: Icons.notifications_none_outlined,
                        message: 'Aucune notification pour le moment',
                        subtitle: 'Les alertes importantes s\'afficheront ici.',
                      ),
                    ],
                  )
                : RefreshIndicator(
                    onRefresh: inbox.refresh,
                    color: SghlColors.humanCareTeal,
                    child: ListView.separated(
                      padding: EdgeInsets.fromLTRB(16, topPad, 16, bottomPad),
                      itemCount: inbox.items.length + 1,
                      separatorBuilder: (_, index) {
                        if (index == 0) return const SizedBox(height: 8);
                        return const SizedBox(height: 10);
                      },
                      itemBuilder: (context, index) {
                        if (index == 0) return _header(inbox);

                        final n = inbox.items[index - 1];
                        return PatientHcCard(
                          onTap: n.lu ? null : () => inbox.markRead(n.id),
                          highlight: !n.lu,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Container(
                                    padding: const EdgeInsets.all(8),
                                    decoration: BoxDecoration(
                                      color: n.lu
                                          ? const Color(0xFFF1F5F9)
                                          : const Color(0xFFD1FAE5),
                                      borderRadius: BorderRadius.circular(10),
                                    ),
                                    child: Icon(
                                      Icons.notifications_rounded,
                                      size: 20,
                                      color: n.lu
                                          ? SghlColors.humanCareMuted
                                          : SghlColors.humanCareTeal,
                                    ),
                                  ),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: Text(
                                      n.titre,
                                      style: Theme.of(context)
                                          .textTheme
                                          .titleMedium
                                          ?.copyWith(
                                            fontWeight: n.lu
                                                ? FontWeight.w600
                                                : FontWeight.w800,
                                          ),
                                    ),
                                  ),
                                  if (!n.lu)
                                    Container(
                                      width: 8,
                                      height: 8,
                                      decoration: const BoxDecoration(
                                        color: Color(0xFF0D9488),
                                        shape: BoxShape.circle,
                                      ),
                                    ),
                                ],
                              ),
                              const SizedBox(height: 10),
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
                        );
                      },
                    ),
                  ),
      ),
    );
  }
}
