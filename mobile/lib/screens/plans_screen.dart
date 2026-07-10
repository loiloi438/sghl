import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../models/patient_models.dart';
import '../services/patient_services.dart';

class PlansScreen extends StatefulWidget {
  const PlansScreen({super.key});

  static const route = '/plans';

  @override
  State<PlansScreen> createState() => _PlansScreenState();
}

class _PlansScreenState extends State<PlansScreen> {
  List<PlanSoins> _items = [];
  bool _loading = true;

  String _statusLabel(String status) {
    switch (status.toLowerCase()) {
      case 'actif':
      case 'active':
        return 'Actif';
      case 'termine':
      case 'terminé':
        return 'Terminé';
      case 'en_attente':
      case 'en attente':
        return 'En attente';
      default:
        return status.isEmpty ? 'Inconnu' : status;
    }
  }

  Color _statusColor(BuildContext context, String status) {
    switch (status.toLowerCase()) {
      case 'actif':
      case 'active':
        return Theme.of(context).colorScheme.primaryContainer;
      case 'termine':
      case 'terminé':
        return Theme.of(context).colorScheme.surfaceContainerHighest;
      case 'en_attente':
      case 'en attente':
        return Theme.of(context).colorScheme.tertiaryContainer;
      default:
        return Theme.of(context).colorScheme.surfaceContainerHighest;
    }
  }

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
    return Scaffold(
      appBar: AppBar(title: const Text('Plans de soins')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _load,
              child: _items.isEmpty
                  ? ListView(
                      children: const [
                        SizedBox(height: 120),
                        Center(child: Text('Aucun plan de soins')),
                      ],
                    )
                  : ListView.separated(
                      padding: const EdgeInsets.all(16),
                      itemCount: _items.length,
                      separatorBuilder: (context, index) =>
                          const SizedBox(height: 8),
                      itemBuilder: (context, index) {
                        final plan = _items[index];
                        return Card(
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Expanded(
                                      child: Text(
                                        plan.titre,
                                        style: Theme.of(
                                          context,
                                        ).textTheme.titleMedium,
                                      ),
                                    ),
                                    const SizedBox(width: 8),
                                    Chip(
                                      label: Text(_statusLabel(plan.statut)),
                                      backgroundColor: _statusColor(
                                        context,
                                        plan.statut,
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 8),
                                Text(plan.description),
                                const SizedBox(height: 8),
                                Text(
                                  'Depuis le ${_formatDate(plan.dateDebut)}',
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
            ),
    );
  }
}
