import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../core/sghl_theme.dart';
import '../models/patient_models.dart';
import '../services/patient_services.dart';
import '../widgets/patient_human_care_page.dart';

class ConstantesScreen extends StatefulWidget {
  const ConstantesScreen({super.key});

  static const route = '/constantes';

  @override
  State<ConstantesScreen> createState() => _ConstantesScreenState();
}

class _ConstantesScreenState extends State<ConstantesScreen> {
  List<ConstanteVitale> _items = [];
  bool _loading = true;

  String _summary(ConstanteVitale c) {
    final parts = <String>[];
    if (c.temperature != null) parts.add('T° ${c.temperature}°C');
    if (c.tensionSystolique != null) {
      parts.add('TA ${c.tensionSystolique}/${c.tensionDiastolique ?? '-'}');
    }
    if (c.frequenceCardiaque != null) parts.add('FC ${c.frequenceCardiaque}');
    if (c.saturationO2 != null) parts.add('SpO₂ ${c.saturationO2}%');
    return parts.isEmpty ? 'Mesure enregistrée' : parts.join(' · ');
  }

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final data = await context.read<PatientService>().fetchConstantes();
      if (mounted) setState(() => _items = data);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  String _formatDate(String iso) {
    try {
      return DateFormat('dd/MM/yyyy HH:mm').format(DateTime.parse(iso).toLocal());
    } catch (_) {
      return iso;
    }
  }

  @override
  Widget build(BuildContext context) {
    return PatientHcListPage(
      title: 'Constantes vitales',
      subtitle: 'Suivi de vos mesures par l\'équipe soignante 💙',
      loading: _loading,
      onRefresh: _load,
      emptyIcon: Icons.monitor_heart_outlined,
      emptyTitle: 'Pas encore de constantes',
      emptySubtitle: 'Vos mesures apparaîtront ici après vos soins.',
      itemCount: _items.length,
      itemBuilder: (context, index) {
        final c = _items[index];
        return PatientHcCard(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: SghlColors.humanCareSand.withValues(alpha: 0.6),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.monitor_heart_outlined, color: Color(0xFFB45309)),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _summary(c),
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700),
                    ),
                    const SizedBox(height: 4),
                    Text(_formatDate(c.mesureLe), style: Theme.of(context).textTheme.bodySmall),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
