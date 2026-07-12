import 'package:flutter/material.dart';

import '../core/sghl_theme.dart';

class RdvStatusStyle {
  const RdvStatusStyle({
    required this.label,
    required this.background,
    required this.border,
    required this.text,
  });

  final String label;
  final Color background;
  final Color border;
  final Color text;
}

RdvStatusStyle rdvStatusStyle(String statut) {
  switch (statut) {
    case 'en_attente':
    case 'planifie':
      return const RdvStatusStyle(
        label: 'En attente de validation',
        background: Color(0xFFFFF7ED),
        border: Color(0xFFFED7AA),
        text: Color(0xFFC2410C),
      );
    case 'confirme':
      return RdvStatusStyle(
        label: 'Validé',
        background: SghlColors.humanCareMint.withValues(alpha: 0.25),
        border: SghlColors.humanCareMint,
        text: const Color(0xFF065F46),
      );
    case 'annule':
      return const RdvStatusStyle(
        label: 'Annulé',
        background: Color(0xFFFEF2F2),
        border: Color(0xFFFECACA),
        text: Color(0xFFB91C1C),
      );
    case 'termine':
      return const RdvStatusStyle(
        label: 'Terminé',
        background: Color(0xFFF0FDF4),
        border: Color(0xFFBBF7D0),
        text: Color(0xFF166534),
      );
    case 'absent':
      return const RdvStatusStyle(
        label: 'Absent',
        background: Color(0xFFFFF7ED),
        border: Color(0xFFFDE68A),
        text: Color(0xFFB45309),
      );
    default:
      return RdvStatusStyle(
        label: statut,
        background: SghlColors.humanCareSky,
        border: const Color(0xFFBAE6FD),
        text: const Color(0xFF0369A1),
      );
  }
}

bool rdvIsPendingValidation(String statut) =>
    statut == 'en_attente' || statut == 'planifie';

bool rdvCanJoinVisio(String statut, {required bool hasLink}) =>
    statut == 'confirme' && hasLink;

bool rdvPeutAnnuler(String statut) =>
    statut == 'en_attente' || statut == 'planifie' || statut == 'confirme';

/// Pastille statut RDV Human-Care.
class SghlRdvStatusChip extends StatelessWidget {
  const SghlRdvStatusChip({super.key, required this.statut});

  final String statut;

  @override
  Widget build(BuildContext context) {
    final style = rdvStatusStyle(statut);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: style.background,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: style.border),
      ),
      child: Text(
        style.label,
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: style.text,
              fontWeight: FontWeight.w700,
            ),
      ),
    );
  }
}
