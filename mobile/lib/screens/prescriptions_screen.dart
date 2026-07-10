import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../models/patient_models.dart';
import '../services/patient_services.dart';
import '../widgets/pdf_download_button.dart';

class PrescriptionsScreen extends StatefulWidget {
  const PrescriptionsScreen({super.key});

  static const route = '/prescriptions';

  @override
  State<PrescriptionsScreen> createState() => _PrescriptionsScreenState();
}

class _PrescriptionsScreenState extends State<PrescriptionsScreen> {
  List<PrescriptionPatient> _items = [];
  bool _loading = true;

  String _statusLabel(String status) {
    switch (status.toLowerCase()) {
      case 'validee':
      case 'validée':
      case 'valide':
        return 'Validée';
      case 'en_attente':
      case 'en attente':
      case 'pending':
        return 'En attente';
      case 'rejetee':
      case 'rejetée':
        return 'Rejetée';
      default:
        return status.isEmpty ? 'Inconnu' : status;
    }
  }

  Color _statusColor(BuildContext context, String status) {
    switch (status.toLowerCase()) {
      case 'validee':
      case 'validée':
      case 'valide':
        return Theme.of(context).colorScheme.primaryContainer;
      case 'en_attente':
      case 'en attente':
      case 'pending':
        return Theme.of(context).colorScheme.tertiaryContainer;
      case 'rejetee':
      case 'rejetée':
        return Theme.of(context).colorScheme.errorContainer;
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
      final data = await context.read<PatientService>().fetchPrescriptions();
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
      appBar: AppBar(title: const Text('Mes prescriptions')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _load,
              child: _items.isEmpty
                  ? ListView(
                      children: const [
                        SizedBox(height: 120),
                        Center(child: Text('Aucune prescription validée')),
                      ],
                    )
                  : ListView.separated(
                      padding: const EdgeInsets.all(16),
                      itemCount: _items.length,
                      separatorBuilder: (context, index) =>
                          const SizedBox(height: 8),
                      itemBuilder: (context, index) {
                        final rx = _items[index];
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
                                        'Prescription du ${_formatDate(rx.valideeLe)}',
                                        style: Theme.of(
                                          context,
                                        ).textTheme.titleMedium,
                                      ),
                                    ),
                                    const SizedBox(width: 8),
                                    Chip(
                                      label: Text(_statusLabel(rx.statut)),
                                      backgroundColor: _statusColor(
                                        context,
                                        rx.statut,
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 8),
                                Text('Médecin : ${rx.medecinNom}'),
                                if (rx.diagnostics.isNotEmpty) ...[
                                  const SizedBox(height: 10),
                                  Text(
                                    'Diagnostics',
                                    style: Theme.of(
                                      context,
                                    ).textTheme.labelLarge,
                                  ),
                                  const SizedBox(height: 4),
                                  ...rx.diagnostics.map(
                                    (d) => Padding(
                                      padding: const EdgeInsets.only(bottom: 4),
                                      child: Text('• $d'),
                                    ),
                                  ),
                                ],
                                if (rx.medicaments.isNotEmpty) ...[
                                  const SizedBox(height: 10),
                                  Text(
                                    'Médicaments',
                                    style: Theme.of(
                                      context,
                                    ).textTheme.labelLarge,
                                  ),
                                  const SizedBox(height: 4),
                                  ...rx.medicaments.map(
                                    (m) => Padding(
                                      padding: const EdgeInsets.only(bottom: 4),
                                      child: Text('• $m'),
                                    ),
                                  ),
                                ],
                                const SizedBox(height: 12),
                                PdfDownloadButton(
                                  label: 'PDF signé',
                                  onDownload: () => context
                                      .read<PatientService>()
                                      .downloadPrescriptionPdf(rx.id),
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
