import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../models/patient_models.dart';
import '../models/staff_models.dart';
import '../core/api_errors.dart';
import '../services/staff_services.dart';

class StaffRdvManageSheet extends StatefulWidget {
  const StaffRdvManageSheet({
    super.key,
    required this.rdv,
    required this.medecins,
    required this.canManage,
    required this.onUpdated,
  });

  final RendezVousStaff rdv;
  final List<MedecinDispo> medecins;
  final bool canManage;
  final ValueChanged<RendezVousStaff> onUpdated;

  @override
  State<StaffRdvManageSheet> createState() => _StaffRdvManageSheetState();
}

class _StaffRdvManageSheetState extends State<StaffRdvManageSheet> {
  late RendezVousStaff _rdv;
  late int _medecinId;
  late DateTime _dateHeure;
  late String _initialDateKey;
  late int _initialMedecinId;
  late String _initialMotif;
  late String _initialNotes;
  late int _initialDuree;

  final _motifController = TextEditingController();
  final _notesController = TextEditingController();
  final _motifModifController = TextEditingController();
  final _motifAnnulController = TextEditingController();

  int _dureeMinutes = 30;
  bool _busy = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _syncFromRdv(widget.rdv);
  }

  @override
  void dispose() {
    _motifController.dispose();
    _notesController.dispose();
    _motifModifController.dispose();
    _motifAnnulController.dispose();
    super.dispose();
  }

  void _syncFromRdv(RendezVousStaff rdv) {
    _rdv = rdv;
    _medecinId = rdv.medecinId;
    _dateHeure = DateTime.parse(rdv.dateHeure).toLocal();
    _dureeMinutes = rdv.dureeMinutes;
    _motifController.text = rdv.motif;
    _notesController.text = rdv.notes;
    _initialDateKey = _dateKey(_dateHeure);
    _initialMedecinId = rdv.medecinId;
    _initialMotif = rdv.motif;
    _initialNotes = rdv.notes;
    _initialDuree = rdv.dureeMinutes;
  }

  String _dateKey(DateTime dt) =>
      '${dt.year}-${dt.month}-${dt.day}-${dt.hour}-${dt.minute}';

  bool get _hasChanges =>
      _dateKey(_dateHeure) != _initialDateKey ||
      _medecinId != _initialMedecinId ||
      _motifController.text.trim() != _initialMotif ||
      _notesController.text.trim() != _initialNotes ||
      _dureeMinutes != _initialDuree;

  bool get _canAct => widget.canManage && _rdv.peutGerer;

  String _formatDateTime(DateTime dt) =>
      DateFormat('dd/MM/yyyy HH:mm').format(dt);

  Future<void> _pickDateTime() async {
    final now = DateTime.now();
    final date = await showDatePicker(
      context: context,
      initialDate: _dateHeure,
      firstDate: now.subtract(const Duration(days: 1)),
      lastDate: now.add(const Duration(days: 365)),
      locale: const Locale('fr', 'FR'),
    );
    if (date == null || !mounted) return;

    final time = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.fromDateTime(_dateHeure),
    );
    if (time == null || !mounted) return;

    setState(() {
      _dateHeure = DateTime(date.year, date.month, date.day, time.hour, time.minute);
    });
  }

  Future<void> _runAction(String action) async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final service = context.read<RendezVousStaffService>();
      RendezVousStaff updated;
      switch (action) {
        case 'confirmer':
          updated = await service.confirmer(rdvId: _rdv.id, version: _rdv.version);
        case 'terminer':
          updated = await service.terminer(rdvId: _rdv.id, version: _rdv.version);
        case 'absent':
          updated = await service.marquerAbsent(rdvId: _rdv.id, version: _rdv.version);
        default:
          return;
      }
      if (!mounted) return;
      setState(() => _syncFromRdv(updated));
      widget.onUpdated(updated);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Rendez-vous mis à jour.')),
      );
    } catch (e) {
      if (mounted) setState(() => _error = friendlyApiError(e));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _submitModifier() async {
    if (!_hasChanges) return;
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final updated = await context.read<RendezVousStaffService>().modifier(
            rdvId: _rdv.id,
            version: _rdv.version,
            dateHeure: _dateKey(_dateHeure) != _initialDateKey ? _dateHeure : null,
            medecinId: _medecinId != _initialMedecinId ? _medecinId : null,
            motif: _motifController.text.trim() != _initialMotif
                ? _motifController.text.trim()
                : null,
            notes: _notesController.text.trim() != _initialNotes
                ? _notesController.text.trim()
                : null,
            dureeMinutes: _dureeMinutes != _initialDuree ? _dureeMinutes : null,
            motifModification: _motifModifController.text,
          );
      if (!mounted) return;
      setState(() => _syncFromRdv(updated));
      widget.onUpdated(updated);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Modification enregistrée — patient notifié si e-mail renseigné.')),
      );
    } catch (e) {
      if (mounted) setState(() => _error = friendlyApiError(e));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _submitAnnuler() async {
    final motif = _motifAnnulController.text.trim();
    if (motif.isEmpty) {
      setState(() => _error = 'Indiquez un motif d\'annulation.');
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final updated = await context.read<RendezVousStaffService>().annuler(
            rdvId: _rdv.id,
            version: _rdv.version,
            motifAnnulation: motif,
          );
      if (!mounted) return;
      setState(() => _syncFromRdv(updated));
      widget.onUpdated(updated);
      Navigator.pop(context);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Rendez-vous annulé.')),
      );
    } catch (e) {
      if (mounted) setState(() => _error = friendlyApiError(e));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.88,
      minChildSize: 0.45,
      maxChildSize: 0.95,
      expand: false,
      builder: (context, scrollController) {
        return Material(
          borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
          child: Column(
            children: [
              const SizedBox(height: 8),
              Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Theme.of(context).dividerColor,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 12, 8, 0),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            _rdv.patientNom,
                            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                  fontWeight: FontWeight.w700,
                                ),
                          ),
                          Text(
                            '${_rdv.numeroDossier} · Dr ${_rdv.medecinNom}',
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                        ],
                      ),
                    ),
                    Chip(label: Text(_rdv.statutLabel)),
                    IconButton(
                      onPressed: () => Navigator.pop(context),
                      icon: const Icon(Icons.close),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: ListView(
                  controller: scrollController,
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
                  children: [
                    if (_error != null) ...[
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Theme.of(context).colorScheme.errorContainer,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(_error!),
                      ),
                      const SizedBox(height: 12),
                    ],
                    Text(
                      'Le patient reçoit un e-mail à chaque modification, report ou annulation (si adresse renseignée).',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                    const SizedBox(height: 16),
                    if (!widget.canManage)
                      const Card(
                        child: ListTile(
                          leading: Icon(Icons.info_outline),
                          title: Text('Lecture seule'),
                          subtitle: Text(
                            'Votre rôle permet de consulter les rendez-vous, pas de les modifier.',
                          ),
                        ),
                      ),
                    if (_canAct) ...[
                      Text('Actions rapides', style: Theme.of(context).textTheme.titleMedium),
                      const SizedBox(height: 8),
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: [
                          if (_rdv.statut == 'en_attente' || _rdv.statut == 'planifie')
                            FilledButton(
                              onPressed: _busy ? null : () => _runAction('confirmer'),
                              child: const Text('Confirmer'),
                            ),
                          if (_rdv.statut == 'confirme')
                            FilledButton(
                              onPressed: _busy ? null : () => _runAction('terminer'),
                              child: const Text('Terminer'),
                            ),
                          if (_rdv.statut == 'en_attente' ||
                              _rdv.statut == 'planifie' ||
                              _rdv.statut == 'confirme')
                            OutlinedButton(
                              onPressed: _busy ? null : () => _runAction('absent'),
                              child: const Text('Absent'),
                            ),
                        ],
                      ),
                      const SizedBox(height: 20),
                      Text('Modifier ou reporter', style: Theme.of(context).textTheme.titleMedium),
                      const SizedBox(height: 8),
                      OutlinedButton.icon(
                        onPressed: _busy ? null : _pickDateTime,
                        icon: const Icon(Icons.calendar_today_outlined),
                        label: Text(_formatDateTime(_dateHeure)),
                      ),
                      const SizedBox(height: 12),
                      DropdownButtonFormField<int>(
                        initialValue: _medecinId,
                        decoration: const InputDecoration(labelText: 'Médecin'),
                        items: widget.medecins
                            .map((m) => DropdownMenuItem(value: m.id, child: Text(m.nom)))
                            .toList(),
                        onChanged: _busy
                            ? null
                            : (v) {
                                if (v != null) setState(() => _medecinId = v);
                              },
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _motifController,
                        decoration: const InputDecoration(labelText: 'Motif'),
                        onChanged: (_) => setState(() {}),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _notesController,
                        decoration: const InputDecoration(labelText: 'Notes internes'),
                        maxLines: 2,
                        onChanged: (_) => setState(() {}),
                      ),
                      const SizedBox(height: 12),
                      DropdownButtonFormField<int>(
                        initialValue: _dureeMinutes,
                        decoration: const InputDecoration(labelText: 'Durée (min)'),
                        items: const [15, 20, 30, 45, 60, 90]
                            .map((d) => DropdownMenuItem(value: d, child: Text('$d min')))
                            .toList(),
                        onChanged: _busy
                            ? null
                            : (v) {
                                if (v != null) setState(() => _dureeMinutes = v);
                              },
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _motifModifController,
                        decoration: const InputDecoration(
                          labelText: 'Motif du report (e-mail patient)',
                          hintText: 'Ex. Médecin indisponible…',
                        ),
                      ),
                      const SizedBox(height: 12),
                      FilledButton(
                        onPressed: _busy || !_hasChanges ? null : _submitModifier,
                        child: _busy
                            ? const SizedBox(
                                height: 20,
                                width: 20,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Text('Enregistrer et notifier'),
                      ),
                      const SizedBox(height: 24),
                      Text('Annuler le rendez-vous', style: Theme.of(context).textTheme.titleMedium),
                      const SizedBox(height: 8),
                      TextField(
                        controller: _motifAnnulController,
                        decoration: const InputDecoration(
                          labelText: 'Motif d\'annulation (e-mail)',
                        ),
                      ),
                      const SizedBox(height: 12),
                      OutlinedButton(
                        style: OutlinedButton.styleFrom(
                          foregroundColor: Theme.of(context).colorScheme.error,
                          side: BorderSide(color: Theme.of(context).colorScheme.error),
                        ),
                        onPressed: _busy ? null : _submitAnnuler,
                        child: const Text('Annuler le rendez-vous'),
                      ),
                    ] else if (widget.canManage && !_rdv.peutGerer)
                      Card(
                        child: ListTile(
                          leading: const Icon(Icons.check_circle_outline),
                          title: Text('Statut : ${_rdv.statutLabel}'),
                          subtitle: Text(_formatDateTime(_dateHeure)),
                        ),
                      ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
