import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../core/api_errors.dart';
import '../core/sghl_theme.dart';
import '../models/patient_models.dart';
import '../services/patient_services.dart';
import '../widgets/human_care_widgets.dart';
import '../widgets/patient_human_care_page.dart';
import 'rendez_vous_screen.dart';

class HospitalisationsScreen extends StatefulWidget {
  const HospitalisationsScreen({super.key});

  static const route = '/hospitalisations';

  @override
  State<HospitalisationsScreen> createState() => _HospitalisationsScreenState();
}

class _HospitalisationsScreenState extends State<HospitalisationsScreen> {
  List<HospitalisationResume> _items = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final data = await context.read<PatientService>().fetchHospitalisations();
      if (mounted) setState(() => _items = data);
    } catch (e) {
      if (mounted) setState(() => _error = friendlyApiError(e));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  String _formatDate(String? iso, {bool short = false}) {
    if (iso == null || iso.isEmpty) return '—';
    try {
      final dt = DateTime.parse(iso).toLocal();
      return short
          ? DateFormat('dd/MM/yyyy').format(dt)
          : DateFormat('dd/MM/yyyy HH:mm').format(dt);
    } catch (_) {
      return iso;
    }
  }

  PatientHcBadgeTone _tone(String statut) {
    switch (statut) {
      case 'active':
        return PatientHcBadgeTone.mint;
      case 'terminee':
        return PatientHcBadgeTone.sky;
      default:
        return PatientHcBadgeTone.alert;
    }
  }

  @override
  Widget build(BuildContext context) {
    return PatientHcListPage(
      title: 'Hospitalisation',
      subtitle: 'Vos séjours passés et en cours, avec l\'équipe qui vous accompagne',
      loading: _loading,
      error: _error,
      onRetry: _load,
      onRefresh: _load,
      emptyIcon: Icons.local_hospital_outlined,
      emptyTitle: 'Vous êtes en bonne santé 💙',
      emptySubtitle:
          'Aucune hospitalisation enregistrée. Nous sommes là si vous avez besoin de nous.',
      headerExtra: _items.isEmpty && !_loading && _error == null
          ? Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: SghlHumanCareButton(
                label: 'Prendre rendez-vous',
                icon: Icons.calendar_month_rounded,
                compact: true,
                onPressed: () =>
                    Navigator.pushNamed(context, RendezVousScreen.route),
              ),
            )
          : null,
      itemCount: _items.length,
      itemBuilder: (context, index) {
        final h = _items[index];
        final sortieLabel = h.dateSortieEffective != null
            ? 'Sortie'
            : h.dateSortiePrevue != null
                ? 'Sortie prévue'
                : null;
        final sortieValue = h.dateSortieEffective ?? h.dateSortiePrevue;

        return PatientHcCard(
          highlight: h.isActive,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        PatientHcBadge(label: h.statutLabel, tone: _tone(h.statut)),
                        const SizedBox(height: 8),
                        Text(
                          h.motifAdmission,
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.w800,
                                color: SghlColors.humanCareText,
                              ),
                        ),
                      ],
                    ),
                  ),
                  if (h.isActive)
                    const Text('🏥', style: TextStyle(fontSize: 28)),
                ],
              ),
              const SizedBox(height: 12),
              _InfoRow(label: 'Admission', value: _formatDate(h.dateAdmission)),
              if (sortieLabel != null)
                _InfoRow(
                  label: sortieLabel,
                  value: _formatDate(sortieValue, short: h.dateSortieEffective == null),
                ),
              _InfoRow(
                label: 'Service',
                value: '${h.serviceNom.isNotEmpty ? h.serviceNom : h.serviceCode} · ${h.batimentCode}',
              ),
              _InfoRow(
                label: 'Médecin référent',
                value: h.medecinNom.isNotEmpty ? h.medecinNom : '—',
              ),
              _InfoRow(
                label: 'Chambre / Lit',
                value: 'Ch. ${h.chambreNumero} · Lit ${h.litNumero}',
              ),
            ],
          ),
        );
      },
    );
  }
}

class _InfoRow extends StatelessWidget {
  const _InfoRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label.toUpperCase(),
            style: Theme.of(context).textTheme.labelSmall?.copyWith(
                  fontWeight: FontWeight.w800,
                  letterSpacing: 0.8,
                  color: SghlColors.humanCareTeal,
                ),
          ),
          Text(value, style: Theme.of(context).textTheme.bodyMedium),
        ],
      ),
    );
  }
}
