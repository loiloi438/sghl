import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../models/patient_models.dart';
import '../services/patient_services.dart';
import '../widgets/human_care_widgets.dart';
import '../widgets/patient_human_care_page.dart';
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
        return 'Payée';
      case 'partiellement_payee':
        return 'Partiellement payée';
      case 'validee':
        return 'En attente';
      default:
        return status;
    }
  }

  PatientHcBadgeTone _tone(String status) {
    switch (status.toLowerCase()) {
      case 'payee':
        return PatientHcBadgeTone.mint;
      case 'partiellement_payee':
        return PatientHcBadgeTone.sand;
      default:
        return PatientHcBadgeTone.sky;
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
        const SnackBar(content: Text('Merci — paiement enregistré 💙')),
      );
    }
  }

  String _formatDate(String? iso) {
    if (iso == null || iso.isEmpty) return '—';
    try {
      return DateFormat('dd/MM/yyyy HH:mm').format(DateTime.parse(iso).toLocal());
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

    return PatientHcListPage(
      title: 'Factures',
      subtitle: 'Historique et téléchargement de vos reçus',
      loading: _loading,
      onRefresh: _load,
      emptyIcon: Icons.receipt_long_outlined,
      emptyTitle: 'Aucune facture',
      emptySubtitle: 'Vos documents de facturation apparaîtront ici.',
      itemCount: _items.length,
      itemBuilder: (context, index) {
        final facture = _items[index];
        return PatientHcCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      facture.numeroFacture ?? 'Facture',
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700),
                    ),
                  ),
                  PatientHcBadge(label: _statusLabel(facture.statut), tone: _tone(facture.statut)),
                ],
              ),
              const SizedBox(height: 8),
              Text('Total : ${_formatMontant(facture.montantTotal)} FCFA'),
              if (facture.payableEnLigne)
                Text(
                  'Reste : ${_formatMontant(facture.montantRestant)} FCFA',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w600),
                ),
              Text('Validée le ${_formatDate(facture.valideeLe)}', style: Theme.of(context).textTheme.bodySmall),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  if (facture.payableEnLigne)
                    SghlHumanCareButton(
                      label: 'Payer en ligne',
                      icon: Icons.payment,
                      compact: true,
                      onPressed: () => _payer(facture),
                    ),
                  PdfDownloadButton(
                    label: 'Facture PDF',
                    onDownload: () => service.downloadFacturePdf(
                      facture.id,
                      numeroFacture: facture.numeroFacture,
                    ),
                  ),
                  if (facture.statut == 'payee' || facture.statut == 'partiellement_payee')
                    PdfDownloadButton(
                      label: 'Reçu PDF',
                      onDownload: () => service.downloadRecuPdf(
                        facture.id,
                        numeroFacture: facture.numeroFacture,
                      ),
                    ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }
}
