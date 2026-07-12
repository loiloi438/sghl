import 'package:flutter/material.dart';

import '../core/sghl_theme.dart';
import 'human_care_widgets.dart';
import 'sghl_design_system.dart';

/// En-tête standard Human-Care pour écrans patient (shell ou plein écran).
class PatientHcHeader extends StatelessWidget {
  const PatientHcHeader({
    super.key,
    required this.title,
    this.subtitle,
    this.embedded = false,
    this.actions,
  });

  final String title;
  final String? subtitle;
  final bool embedded;
  final List<Widget>? actions;

  @override
  Widget build(BuildContext context) {
    if (!embedded) {
      return const SizedBox.shrink();
    }
    return Padding(
      padding: const EdgeInsets.only(top: 48, bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '🌿 Human-Care',
                  style: Theme.of(context).textTheme.labelLarge,
                ),
                const SizedBox(height: 4),
                Text(
                  title,
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w800,
                      ),
                ),
                if (subtitle != null) ...[
                  const SizedBox(height: 4),
                  Text(subtitle!, style: Theme.of(context).textTheme.bodySmall),
                ],
              ],
            ),
          ),
          if (actions != null) ...actions!,
        ],
      ),
    );
  }
}

/// Badge statut pastel Human-Care.
class PatientHcBadge extends StatelessWidget {
  const PatientHcBadge({
    super.key,
    required this.label,
    this.tone = PatientHcBadgeTone.mint,
  });

  final String label;
  final PatientHcBadgeTone tone;

  @override
  Widget build(BuildContext context) {
    final (bg, fg) = switch (tone) {
      PatientHcBadgeTone.mint => (
          const Color(0xFFD1FAE5),
          const Color(0xFF065F46),
        ),
      PatientHcBadgeTone.sky => (
          const Color(0xFFBAE6FD),
          const Color(0xFF0C4A6E),
        ),
      PatientHcBadgeTone.sand => (
          const Color(0xFFFEF3C7),
          const Color(0xFF92400E),
        ),
      PatientHcBadgeTone.alert => (
          const Color(0xFFFEE2E2),
          const Color(0xFF991B1B),
        ),
    };
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: fg,
              fontWeight: FontWeight.w800,
            ),
      ),
    );
  }
}

enum PatientHcBadgeTone { mint, sky, sand, alert }

/// Carte liste Human-Care.
class PatientHcCard extends StatelessWidget {
  const PatientHcCard({
    super.key,
    required this.child,
    this.onTap,
    this.highlight = false,
  });

  final Widget child;
  final VoidCallback? onTap;
  final bool highlight;

  @override
  Widget build(BuildContext context) {
    return SghlCard(
      lightSurface: true,
      padding: const EdgeInsets.all(14),
      onTap: onTap,
      child: DecoratedBox(
        decoration: highlight
            ? BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF99F6E4), width: 1.5),
              )
            : const BoxDecoration(),
        child: Padding(
          padding: highlight ? const EdgeInsets.all(4) : EdgeInsets.zero,
          child: child,
        ),
      ),
    );
  }
}

/// Scaffold liste patient Human-Care (thème appliqué par le parent).
class PatientHcListPage extends StatelessWidget {
  const PatientHcListPage({
    super.key,
    required this.title,
    this.subtitle,
    this.embedded = false,
    required this.loading,
    required this.onRefresh,
    this.error,
    this.onRetry,
    this.emptyIcon = Icons.medical_services_outlined,
    this.emptyTitle = 'Rien à afficher',
    this.emptySubtitle,
    required this.itemCount,
    required this.itemBuilder,
    this.headerExtra,
    this.actions,
    this.bottomPadding = 16,
    this.floatingAction,
  });

  final String title;
  final String? subtitle;
  final bool embedded;
  final bool loading;
  final Future<void> Function() onRefresh;
  final String? error;
  final VoidCallback? onRetry;
  final IconData emptyIcon;
  final String emptyTitle;
  final String? emptySubtitle;
  final int itemCount;
  final IndexedWidgetBuilder itemBuilder;
  final Widget? headerExtra;
  final List<Widget>? actions;
  final double bottomPadding;
  final Widget? floatingAction;

  @override
  Widget build(BuildContext context) {
    final topPad = embedded ? 8.0 : 16.0;
    final headerCount = (embedded ? 1 : 0) + (headerExtra != null ? 1 : 0);

    Widget body;
    if (loading && itemCount == 0 && error == null) {
      body = const Center(child: CircularProgressIndicator());
    } else if (error != null && itemCount == 0) {
      body = ListView(
        padding: EdgeInsets.fromLTRB(16, topPad, 16, bottomPadding),
        children: [
          if (embedded)
            PatientHcHeader(title: title, subtitle: subtitle, actions: actions),
          SghlFeedbackBanner(message: error!, type: SghlFeedbackType.error),
          const SizedBox(height: 16),
          SghlHumanCareButton(label: 'Réessayer', onPressed: onRetry ?? onRefresh),
        ],
      );
    } else if (itemCount == 0) {
      body = ListView(
        padding: EdgeInsets.fromLTRB(16, topPad, 16, bottomPadding),
        children: [
          if (embedded)
            PatientHcHeader(title: title, subtitle: subtitle, actions: actions),
          if (headerExtra != null) headerExtra!,
          SghlEmptyState(
            icon: emptyIcon,
            message: emptyTitle,
            subtitle: emptySubtitle,
          ),
        ],
      );
    } else {
      body = RefreshIndicator(
        onRefresh: onRefresh,
        color: SghlColors.humanCareTeal,
        child: ListView.separated(
          padding: EdgeInsets.fromLTRB(16, topPad, 16, bottomPadding),
          itemCount: itemCount + headerCount,
          separatorBuilder: (_, index) {
            if (index < headerCount) return const SizedBox(height: 8);
            return const SizedBox(height: 10);
          },
          itemBuilder: (context, index) {
            if (embedded && index == 0) {
              return PatientHcHeader(
                title: title,
                subtitle: subtitle,
                actions: actions,
              );
            }
            if (headerExtra != null && index == (embedded ? 1 : 0)) {
              return headerExtra!;
            }
            final dataIndex = index - headerCount;
            return itemBuilder(context, dataIndex);
          },
        ),
      );
    }

    return Scaffold(
      appBar: embedded
          ? null
          : AppBar(
              title: Text(title),
              actions: actions,
            ),
      floatingActionButton: floatingAction,
      body: SghlHumanCareBackground(child: body),
    );
  }
}

/// Applique le thème Human-Care à un écran patient (routes hors shell).
class PatientHumanCareTheme extends StatelessWidget {
  const PatientHumanCareTheme({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Theme(data: SghlTheme.patientHumanCare(), child: child);
  }
}
