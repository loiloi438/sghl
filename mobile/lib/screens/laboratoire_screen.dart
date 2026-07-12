import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../models/patient_models.dart';
import '../services/patient_services.dart';
import '../widgets/patient_human_care_page.dart';
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

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final data = await context.read<PatientService>().fetchResultatsLaboratoire();
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
      title: 'Laboratoire',
      subtitle: 'Résultats d\'analyses publiés par le laboratoire',
      loading: _loading,
      onRefresh: _load,
      emptyIcon: Icons.biotech_outlined,
      emptyTitle: 'Aucun résultat publié',
      emptySubtitle: 'Vos analyses apparaîtront ici dès leur validation.',
      itemCount: _items.length,
      itemBuilder: (context, index) {
        final item = _items[index];
        return PatientHcCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Text('🔬', style: TextStyle(fontSize: 26)),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const PatientHcBadge(label: 'Publié', tone: PatientHcBadgeTone.sky),
                        const SizedBox(height: 6),
                        Text(
                          'Dr ${item.medecinNom}',
                          style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700),
                        ),
                        Text(
                          'Publié le ${_formatDate(item.publieeLe)}',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              if (item.analyses.isNotEmpty) ...[
                const SizedBox(height: 10),
                ...item.analyses.map(
                  (a) => Container(
                    width: double.infinity,
                    margin: const EdgeInsets.only(bottom: 6),
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: const Color(0xFFE0F2FE),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(a, style: const TextStyle(fontFamily: 'monospace', fontSize: 12)),
                  ),
                ),
              ],
              const SizedBox(height: 12),
              PdfDownloadButton(
                label: 'PDF résultats',
                onDownload: () => context.read<PatientService>().downloadLaboPdf(item.id),
              ),
            ],
          ),
        );
      },
    );
  }
}
