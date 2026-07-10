import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../models/patient_models.dart';
import '../services/patient_services.dart';
import '../widgets/patient_payment_sheet.dart';
import '../widgets/pdf_download_button.dart';

class FacturesScreen extends StatefulWidget {
  const FacturesScreen({super.key});

  static const route = '/factures';

  @override
  State<FacturesScreen> createState() => _FacturesScreenState();
}

class _FacturesScreenState extends State<FacturesScreen> {
  List<FacturePatient> _items = [];
  bool _loading = true;

  String _statusLabel(String status) {
    switch (status.toLowerCase()) {
      case 'payee':
      case 'payée':
      case 'paye':
        return 'Payée';
      case 'partiellement_payee':
      case 'partiellement payée':
        return 'Partiellement payée';
      case 'validee':
      case 'validée':
      case 'valide':
        return 'Validée';
      case 'en_attente':
      case 'en attente':
      case 'pending':
        return 'En attente';
      default:
        return status.isEmpty ? 'Inconnu' : status;
    }
  }

  Color _statusColor(BuildContext context, String status) {
    switch (status.toLowerCase()) {
      case 'payee':
      case 'payée':
      case 'paye':
        return Theme.of(context).colorScheme.primaryContainer;
      case 'partiellement_payee':
      case 'partiellement payée':
        return Theme.of(context).colorScheme.secondaryContainer;
      case 'validee':
      case 'validée':
      case 'valide':
        return Theme.of(context).colorScheme.tertiaryContainer;
      case 'en_attente':
      case 'en attente':
      case 'pending':
        return Theme.of(context).colorScheme.surfaceContainerHighest;
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
      final data = await context.read<PatientService>().fetchFactures();
      if (mounted) setState(() => _items = data);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _payer(FacturePatient facture) async {
    final success = await showPatientPaymentSheet(context, facture: facture);
    if (success == true && mounted) {
      await _load();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Facture mise à jour.')),
      );
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

  String _formatMontant(String value) {
    final n = num.tryParse(value);
    if (n == null) return value;
    return NumberFormat('#,##0.00', 'fr_FR').format(n);
  }

  @override
  Widget build(BuildContext context) {
    final service = context.read<PatientService>();

    return Scaffold(
      appBar: AppBar(title: const Text('Mes factures')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _load,
              child: _items.isEmpty
                  ? ListView(
                      children: const [
                        SizedBox(height: 120),
                        Center(child: Text('Aucune facture disponible')),
                      ],
                    )
                  : ListView.separated(
                      padding: const EdgeInsets.all(16),
                      itemCount: _items.length,
                      separatorBuilder: (context, index) =>
                          const SizedBox(height: 8),
                      itemBuilder: (context, index) {
                        final facture = _items[index];
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
                                        facture.numeroFacture ?? 'Facture',
                                        style: Theme.of(
                                          context,
                                        ).textTheme.titleMedium,
                                      ),
                                    ),
                                    const SizedBox(width: 8),
                                    Chip(
                                      label: Text(_statusLabel(facture.statut)),
                                      backgroundColor: _statusColor(
                                        context,
                                        facture.statut,
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  'Montant total : ${_formatMontant(facture.montantTotal)} FCFA',
                                  style: Theme.of(context).textTheme.titleSmall,
                                ),
                                if (facture.montantPaye != '0' &&
                                    facture.montantPaye != '0.00')
                                  Text(
                                    'Déjà payé : ${_formatMontant(facture.montantPaye)} FCFA',
                                  ),
                                if (facture.payableEnLigne)
                                  Text(
                                    'Reste à payer : ${_formatMontant(facture.montantRestant)} FCFA',
                                    style: Theme.of(context)
                                        .textTheme
                                        .bodyMedium
                                        ?.copyWith(fontWeight: FontWeight.w600),
                                  ),
                                const SizedBox(height: 4),
                                Text(
                                  'Validée le ${_formatDate(facture.valideeLe)}',
                                ),
                                if (facture.payeeLe != null)
                                  Text(
                                    'Payée le ${_formatDate(facture.payeeLe)}',
                                  ),
                                const SizedBox(height: 12),
                                Wrap(
                                  spacing: 8,
                                  runSpacing: 8,
                                  children: [
                                    if (facture.payableEnLigne)
                                      FilledButton.icon(
                                        onPressed: () => _payer(facture),
                                        icon: const Icon(Icons.payment),
                                        label: const Text('Payer en ligne'),
                                      ),
                                    PdfDownloadButton(
                                      label: 'PDF signé',
                                      onDownload: () =>
                                          service.downloadFacturePdf(
                                        facture.id,
                                        numeroFacture: facture.numeroFacture,
                                      ),
                                    ),
                                  ],
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
