import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../models/patient_models.dart';
import '../services/patient_services.dart';

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
    return Scaffold(
      appBar: AppBar(title: const Text('Rappels médicamenteux')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _load,
              child: _items.isEmpty
                  ? ListView(
                      children: const [
                        SizedBox(height: 120),
                        Center(child: Text('Aucun médicament planifié')),
                      ],
                    )
                  : ListView.separated(
                      padding: const EdgeInsets.all(16),
                      itemCount: _items.length,
                      separatorBuilder: (context, index) => const SizedBox(height: 8),
                      itemBuilder: (context, index) {
                        final dose = _items[index];
                        return Card(
                          color: dose.estEnRetard
                              ? Colors.orange.shade50
                              : null,
                          child: ListTile(
                            leading: Icon(
                              dose.estEnRetard
                                  ? Icons.notifications_active_outlined
                                  : Icons.medication_liquid_outlined,
                              color: dose.estEnRetard ? Colors.orange.shade800 : null,
                            ),
                            title: Text(dose.medicament),
                            subtitle: Text('${dose.posologie} — ${_formatDate(dose.heurePrevue)}'),
                            trailing: dose.estEnRetard
                                ? const Text('À prendre', style: TextStyle(color: Colors.orange))
                                : null,
                          ),
                        );
                      },
                    ),
            ),
    );
  }
}
