import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../models/patient_models.dart';
import '../services/patient_services.dart';
import '../widgets/pdf_download_button.dart';

class LaboratoireScreen extends StatefulWidget {
  const LaboratoireScreen({super.key});

  static const route = '/laboratoire';

  @override
  State<LaboratoireScreen> createState() => _LaboratoireScreenState();
}

class _LaboratoireScreenState extends State<LaboratoireScreen> {
  List<ResultatLaboPatient> _items = [];
  bool _loading = true;

  String _statusLabel(String status) {
    switch (status.toLowerCase()) {
      case 'publie':
      case 'publié':
      case 'final':
        return 'Publié';
      case 'en_cours':
      case 'en cours':
      case 'pending':
        return 'En cours';
      default:
        return status.isEmpty ? 'Inconnu' : status;
    }
  }

  Color _statusColor(BuildContext context, String status) {
    switch (status.toLowerCase()) {
      case 'publie':
      case 'publié':
      case 'final':
        return Theme.of(context).colorScheme.primaryContainer;
      case 'en_cours':
      case 'en cours':
      case 'pending':
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
      final data = await context
          .read<PatientService>()
          .fetchResultatsLaboratoire();
      if (mounted) setState(() => _items = data);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  String _formatDate(String? iso) {
    if (iso == null || iso.isEmpty) return '—';
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
      appBar: AppBar(title: const Text('Résultats laboratoire')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _load,
              child: _items.isEmpty
                  ? ListView(
                      children: const [
                        SizedBox(height: 120),
                        Center(child: Text('Aucun résultat publié')),
                      ],
                    )
                  : ListView.separated(
                      padding: const EdgeInsets.all(16),
                      itemCount: _items.length,
                      separatorBuilder: (context, index) =>
                          const SizedBox(height: 8),
                      itemBuilder: (context, index) {
                        final item = _items[index];
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
                                        'Publié le ${_formatDate(item.publieeLe)}',
                                        style: Theme.of(
                                          context,
                                        ).textTheme.titleMedium,
                                      ),
                                    ),
                                    const SizedBox(width: 8),
                                    Chip(
                                      label: Text(_statusLabel(item.statut)),
                                      backgroundColor: _statusColor(
                                        context,
                                        item.statut,
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 8),
                                Text('Prescrit par : ${item.medecinNom}'),
                                const SizedBox(height: 10),
                                Text(
                                  'Analyses',
                                  style: Theme.of(context).textTheme.labelLarge,
                                ),
                                const SizedBox(height: 4),
                                ...item.analyses.map(
                                  (a) => Padding(
                                    padding: const EdgeInsets.only(bottom: 4),
                                    child: Text('• $a'),
                                  ),
                                ),
                                const SizedBox(height: 12),
                                PdfDownloadButton(
                                  label: 'PDF signé',
                                  onDownload: () => context
                                      .read<PatientService>()
                                      .downloadLaboPdf(item.id),
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
