import 'package:flutter/material.dart';

import 'package:intl/intl.dart';

import 'package:provider/provider.dart';



import '../core/sghl_theme.dart';

import '../services/notification_inbox_service.dart';

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

    final bottomPad =

        widget.embedded ? kPatientShellBottomPadding : 16.0;



    return Scaffold(

      appBar: widget.embedded

          ? null

          : AppBar(

              title: const Text('Notifications'),

              actions: [

                IconButton(

                  onPressed: inbox.loading ? null : () => inbox.refresh(),

                  icon: const Icon(Icons.refresh_rounded),

                ),

              ],

            ),

      body: inbox.loading && inbox.items.isEmpty

          ? const Center(child: CircularProgressIndicator())

          : inbox.items.isEmpty

              ? ListView(

                  padding: EdgeInsets.fromLTRB(16, 48, 16, bottomPad),

                  children: [

                    if (widget.embedded) ...[

                      Row(

                        children: [

                          Expanded(

                            child: Text(

                              'Alertes',

                              style:

                                  Theme.of(context).textTheme.headlineSmall,

                            ),

                          ),

                          IconButton(

                            onPressed:

                                inbox.loading ? null : () => inbox.refresh(),

                            icon: const Icon(Icons.refresh_rounded),

                          ),

                        ],

                      ),

                      const SizedBox(height: 8),

                      Text(

                        'Rappels, confirmations et messages de l\'hôpital.',

                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(

                              color: Theme.of(context).colorScheme.outline,

                            ),

                      ),

                      const SizedBox(height: 24),

                    ],

                    const SghlCard(
                      lightSurface: true,

                      padding: EdgeInsets.all(20),

                      child: Center(

                        child: Text(

                          'Aucune notification pour le moment.',

                        ),

                      ),

                    ),

                  ],

                )

              : RefreshIndicator(

                  onRefresh: inbox.refresh,

                  child: ListView.separated(

                    padding: EdgeInsets.fromLTRB(

                      16,

                      widget.embedded ? 48 : 16,

                      16,

                      bottomPad,

                    ),

                    itemCount: inbox.items.length + (widget.embedded ? 1 : 0),

                    separatorBuilder: (_, __) => const SizedBox(height: 10),

                    itemBuilder: (context, index) {

                      if (widget.embedded && index == 0) {

                        return Column(

                          crossAxisAlignment: CrossAxisAlignment.start,

                          children: [

                            Row(

                              children: [

                                Expanded(

                                  child: Text(

                                    'Alertes',

                                    style: Theme.of(context)

                                        .textTheme

                                        .headlineSmall,

                                  ),

                                ),

                                IconButton(

                                  onPressed: inbox.loading

                                      ? null

                                      : () => inbox.refresh(),

                                  icon: const Icon(Icons.refresh_rounded),

                                ),

                              ],

                            ),

                            const SizedBox(height: 8),

                            Text(

                              'Rappels, confirmations et messages de l\'hôpital.',

                              style: Theme.of(context)

                                  .textTheme

                                  .bodyMedium

                                  ?.copyWith(

                                color:

                                    Theme.of(context).colorScheme.outline,

                              ),

                            ),

                            const SizedBox(height: 16),

                          ],

                        );

                      }



                      final n = inbox.items[widget.embedded ? index - 1 : index];

                      return SghlCard(
                        lightSurface: true,

                        padding: const EdgeInsets.all(14),

                        onTap: n.lu ? null : () => inbox.markRead(n.id),

                        child: Column(

                          crossAxisAlignment: CrossAxisAlignment.start,

                          children: [

                            Row(

                              children: [

                                Container(

                                  padding: const EdgeInsets.all(8),

                                  decoration: BoxDecoration(

                                    color: n.lu

                                        ? Theme.of(context)

                                            .colorScheme

                                            .outline

                                            .withValues(alpha: 0.1)

                                        : SghlColors.mintGreen

                                            .withValues(alpha: 0.25),

                                    borderRadius: BorderRadius.circular(10),

                                  ),

                                  child: Icon(

                                    Icons.notifications_rounded,

                                    size: 20,

                                    color: n.lu

                                        ? Theme.of(context).colorScheme.outline

                                        : SghlColors.medicalBlue,

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
                                              : FontWeight.w700,
                                        ),

                                  ),

                                ),

                                if (!n.lu)

                                  Container(

                                    width: 8,

                                    height: 8,

                                    decoration: const BoxDecoration(

                                      color: SghlColors.coral,

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

    );

  }

}


