import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../models/patient_models.dart';
import '../services/patient_services.dart';
import '../widgets/patient_human_care_page.dart';

class PlansScreen extends StatefulWidget {
  const PlansScreen({super.key});

  static const route = '/plans';

  @override
  State<PlansScreen> createState() => _PlansScreenState();
}

class _PlansScreenState extends State<PlansScreen> {
  List<PlanSoins> _items = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final data = await context.read<PatientService>().fetchPlansSoins();
      if (mounted) setState(() => _items = data);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  String _formatDate(String iso) {
    try {
      return DateFormat('dd/MM/yyyy').format(DateTime.parse(iso).toLocal());
    } catch (_) {
      return iso;
    }
  }

  @override
  Widget build(BuildContext context) {
    return PatientHcListPage(
      title: 'Plans de soins',
      subtitle: 'Votre parcours de soins personnalisé',
      loading: _loading,
      onRefresh: _load,
      emptyIcon: Icons.medical_services_outlined,
      emptyTitle: 'Aucun plan de soins',
      emptySubtitle: 'Votre équipe soignante élabore un plan adapté à vos besoins.',
      itemCount: _items.length,
      itemBuilder: (context, index) {
        final plan = _items[index];
        return PatientHcCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      plan.titre,
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700),
                    ),
                  ),
                  PatientHcBadge(label: plan.statut, tone: PatientHcBadgeTone.sky),
                ],
              ),
              const SizedBox(height: 8),
              Text(plan.description),
              const SizedBox(height: 8),
              Text('Depuis le ${_formatDate(plan.dateDebut)}', style: Theme.of(context).textTheme.bodySmall),
            ],
          ),
        );
      },
    );
  }
}
