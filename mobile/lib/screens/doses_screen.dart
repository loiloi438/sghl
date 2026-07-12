import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../models/patient_models.dart';
import '../services/patient_services.dart';
import '../widgets/patient_human_care_page.dart';

class DosesScreen extends StatefulWidget {
  const DosesScreen({super.key});

  static const route = '/doses';

  @override
  State<DosesScreen> createState() => _DosesScreenState();
}

class _DosesScreenState extends State<DosesScreen> {
  List<DoseMedicament> _items = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final data = await context.read<PatientService>().fetchDoses();
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
      title: 'Soins infirmiers',
      subtitle: 'Planning de vos médicaments et soins',
      loading: _loading,
      onRefresh: _load,
      emptyIcon: Icons.medication_outlined,
      emptyTitle: 'Aucun soin planifié',
      emptySubtitle: 'Votre infirmière vous informera dès qu\'un soin sera programmé.',
      itemCount: _items.length,
      itemBuilder: (context, index) {
        final dose = _items[index];
        return PatientHcCard(
          highlight: dose.estEnRetard,
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(dose.estEnRetard ? '⚠️' : '💉', style: const TextStyle(fontSize: 22)),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            dose.medicament,
                            style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700),
                          ),
                        ),
                        PatientHcBadge(
                          label: dose.estEnRetard ? 'En retard' : dose.statut,
                          tone: dose.estEnRetard ? PatientHcBadgeTone.alert : PatientHcBadgeTone.mint,
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(dose.posologie),
                    const SizedBox(height: 4),
                    Text('🕐 ${_formatDate(dose.heurePrevue)}', style: Theme.of(context).textTheme.bodySmall),
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
