import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../models/patient_models.dart';
import '../services/patient_services.dart';

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
    return parts.isEmpty ? 'Données disponibles' : parts.join(' · ');
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
      return DateFormat(
        'dd/MM/yyyy HH:mm',
      ).format(DateTime.parse(iso).toLocal());
    } catch (_) {
      return iso;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Constantes vitales')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _load,
              child: _items.isEmpty
                  ? ListView(
                      children: const [
                        SizedBox(height: 120),
                        Center(child: Text('Historique vide')),
                      ],
                    )
                  : ListView.separated(
                      padding: const EdgeInsets.all(16),
                      itemCount: _items.length,
                      separatorBuilder: (context, index) =>
                          const SizedBox(height: 8),
                      itemBuilder: (context, index) {
                        final c = _items[index];
                        return Card(
                          child: ListTile(
                            leading: const Icon(Icons.monitor_heart_outlined),
                            title: Text(_formatDate(c.mesureLe)),
                            subtitle: Text(_summary(c)),
                          ),
                        );
                      },
                    ),
            ),
    );
  }
}
