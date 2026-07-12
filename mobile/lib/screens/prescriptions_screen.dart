import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../models/patient_models.dart';
import '../services/patient_services.dart';
import '../widgets/patient_human_care_page.dart';
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

  PatientHcBadgeTone _pharmacieTone(String statut) {
    switch (statut) {
      case 'validee':
        return PatientHcBadgeTone.mint;
      case 'retiree':
        return PatientHcBadgeTone.sky;
      default:
        return PatientHcBadgeTone.sand;
    }
  }

  PatientHcBadgeTone _tone(String statut) {
    switch (statut.toLowerCase()) {
      case 'validee':
        return PatientHcBadgeTone.mint;
      case 'brouillon':
        return PatientHcBadgeTone.sand;
      case 'annulee':
        return PatientHcBadgeTone.alert;
      default:
        return PatientHcBadgeTone.sky;
    }
  }

  String _label(String statut) {
    switch (statut.toLowerCase()) {
      case 'validee':
        return 'Validée';
      case 'brouillon':
        return 'En attente';
      case 'annulee':
        return 'Annulée';
      default:
        return statut;
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
      return DateFormat('dd/MM/yyyy HH:mm').format(DateTime.parse(iso).toLocal());
    } catch (_) {
      return iso;
    }
  }

  @override
  Widget build(BuildContext context) {
    return PatientHcListPage(
      title: 'Pharmacie',
      subtitle: 'Vos ordonnances et leur disponibilité',
      loading: _loading,
      onRefresh: _load,
      emptyIcon: Icons.medication_outlined,
      emptyTitle: 'Aucune prescription',
      emptySubtitle: 'Vos ordonnances apparaîtront ici dès qu\'elles seront disponibles.',
      itemCount: _items.length,
      itemBuilder: (context, index) {
        final rx = _items[index];
        return PatientHcCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('💊', style: TextStyle(fontSize: 28)),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        PatientHcBadge(label: _label(rx.statut), tone: _tone(rx.statut)),
                        const SizedBox(height: 4),
                        PatientHcBadge(
                          label: rx.statutPharmacieLabel,
                          tone: _pharmacieTone(rx.statutPharmacie),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          'Dr ${rx.medecinNom}',
                          style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700),
                        ),
                        Text(
                          rx.valideeLe != null ? 'Validée le ${_formatDate(rx.valideeLe)}' : 'En cours de validation',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              if (rx.medicaments.isNotEmpty) ...[
                const SizedBox(height: 10),
                ...rx.medicaments.map(
                  (m) => Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Text('• $m'),
                  ),
                ),
              ],
              if (rx.statut == 'validee') ...[
                const SizedBox(height: 12),
                PdfDownloadButton(
                  label: 'PDF ordonnance',
                  onDownload: () => context.read<PatientService>().downloadPrescriptionPdf(rx.id),
                ),
              ],
            ],
          ),
        );
      },
    );
  }
}
