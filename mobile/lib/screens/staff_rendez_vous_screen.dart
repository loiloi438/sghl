import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../models/patient_models.dart';
import '../models/staff_models.dart';
import '../services/patient_services.dart';
import '../core/api_errors.dart';
import '../services/staff_services.dart';
import '../widgets/staff_rdv_manage_sheet.dart';

class StaffRendezVousScreen extends StatefulWidget {
  const StaffRendezVousScreen({super.key});

  static const route = '/staff-rendez-vous';

  @override
  State<StaffRendezVousScreen> createState() => _StaffRendezVousScreenState();
}

class _StaffRendezVousScreenState extends State<StaffRendezVousScreen> {
  List<RendezVousStaff> _items = [];
  List<JourSemaine> _semaine = [];
  List<MedecinDispo> _medecins = [];
  bool _loading = true;
  String? _error;

  late DateTime _filterDate;
  String _filterStatut = '';

  @override
  void initState() {
    super.initState();
    _filterDate = DateTime.now();
    _load();
  }

  String get _dateIso => DateFormat('yyyy-MM-dd').format(_filterDate);

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final service = context.read<RendezVousStaffService>();
      final auth = context.read<AuthService>();
      final futures = <Future>[
        service.fetchList(date: _dateIso, statut: _filterStatut.isEmpty ? null : _filterStatut),
        service.fetchSemaine(anchorDate: _dateIso),
      ];
      if (auth.canManageRdv) {
        futures.add(service.fetchMedecins());
      }
      final results = await Future.wait(futures);
      if (!mounted) return;
      setState(() {
        _items = results[0] as List<RendezVousStaff>;
        _semaine = results[1] as List<JourSemaine>;
        _medecins = auth.canManageRdv && results.length > 2
            ? results[2] as List<MedecinDispo>
            : <MedecinDispo>[];
      });
    } catch (e) {
      if (mounted) setState(() => _error = friendlyApiError(e));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  String _formatTime(String iso) {
    try {
      return DateFormat('HH:mm').format(DateTime.parse(iso).toLocal());
    } catch (_) {
      return iso;
    }
  }

  static const _jours = ['lun', 'mar', 'mer', 'jeu', 'ven', 'sam', 'dim'];

  String _dayLabel(String isoDate) {
    try {
      final d = DateTime.parse(isoDate);
      return '${_jours[d.weekday - 1]} ${d.day}';
    } catch (_) {
      return isoDate;
    }
  }

  Future<void> _pickDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _filterDate,
      firstDate: DateTime.now().subtract(const Duration(days: 30)),
      lastDate: DateTime.now().add(const Duration(days: 120)),
      locale: const Locale('fr', 'FR'),
    );
    if (picked == null || !mounted) return;
    setState(() => _filterDate = picked);
    await _load();
  }

  void _selectDay(String isoDate) {
    setState(() => _filterDate = DateTime.parse(isoDate));
    _load();
  }

  void _openManage(RendezVousStaff rdv) {
    final auth = context.read<AuthService>();
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (ctx) => StaffRdvManageSheet(
        rdv: rdv,
        medecins: _medecins,
        canManage: auth.canManageRdv,
        onUpdated: (updated) {
          setState(() {
            final i = _items.indexWhere((r) => r.id == updated.id);
            if (i >= 0) _items[i] = updated;
          });
        },
      ),
    );
  }

  Color? _statutColor(String statut, BuildContext context) {
    switch (statut) {
      case 'en_attente':
        return Colors.orange.shade800;
      case 'confirme':
        return Theme.of(context).colorScheme.primary;
      case 'planifie':
        return Colors.blue.shade700;
      case 'annule':
        return Theme.of(context).colorScheme.error;
      case 'termine':
        return Colors.green.shade700;
      case 'absent':
        return Colors.orange.shade800;
      default:
        return null;
    }
  }

  @override
  Widget build(BuildContext context) {
    final canManage = context.watch<AuthService>().canManageRdv;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Rendez-vous'),
        actions: [
          IconButton(onPressed: _loading ? null : _load, icon: const Icon(Icons.refresh)),
        ],
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SizedBox(
            height: 72,
            child: _semaine.isEmpty && !_loading
                ? const SizedBox.shrink()
                : ListView.separated(
                    scrollDirection: Axis.horizontal,
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    itemCount: _semaine.length,
                    separatorBuilder: (_, __) => const SizedBox(width: 8),
                    itemBuilder: (context, index) {
                      final day = _semaine[index];
                      final selected = day.date == _dateIso;
                      return FilterChip(
                        label: Text('${_dayLabel(day.date)}${day.count > 0 ? ' (${day.count})' : ''}'),
                        selected: selected,
                        onSelected: (_) => _selectDay(day.date),
                      );
                    },
                  ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _pickDate,
                    icon: const Icon(Icons.calendar_today_outlined, size: 18),
                    label: Text(DateFormat('dd/MM/yyyy').format(_filterDate)),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: DropdownButtonFormField<String>(
                    initialValue: _filterStatut,
                    decoration: const InputDecoration(
                      labelText: 'Statut',
                      isDense: true,
                      contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    ),
                    items: const [
                      DropdownMenuItem(value: '', child: Text('Tous')),
                      DropdownMenuItem(value: 'en_attente', child: Text('En attente')),
                      DropdownMenuItem(value: 'planifie', child: Text('Planifié')),
                      DropdownMenuItem(value: 'confirme', child: Text('Confirmé')),
                      DropdownMenuItem(value: 'termine', child: Text('Terminé')),
                      DropdownMenuItem(value: 'annule', child: Text('Annulé')),
                      DropdownMenuItem(value: 'absent', child: Text('Absent')),
                    ],
                    onChanged: _loading
                        ? null
                        : (v) {
                            setState(() => _filterStatut = v ?? '');
                            _load();
                          },
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator())
                : RefreshIndicator(
                    onRefresh: _load,
                    child: _error != null
                        ? ListView(
                            children: [
                              const SizedBox(height: 80),
                              Center(child: Text(_error!, textAlign: TextAlign.center)),
                              const SizedBox(height: 12),
                              Center(
                                child: FilledButton(onPressed: _load, child: const Text('Réessayer')),
                              ),
                            ],
                          )
                        : _items.isEmpty
                            ? ListView(
                                children: const [
                                  SizedBox(height: 80),
                                  Center(child: Text('Aucun rendez-vous pour cette date')),
                                ],
                              )
                            : ListView.separated(
                                padding: const EdgeInsets.all(16),
                                itemCount: _items.length,
                                separatorBuilder: (_, __) => const SizedBox(height: 8),
                                itemBuilder: (context, index) {
                                  final rdv = _items[index];
                                  return Card(
                                    child: ListTile(
                                      leading: CircleAvatar(
                                        backgroundColor:
                                            _statutColor(rdv.statut, context)?.withValues(alpha: 0.15),
                                        child: Text(
                                          _formatTime(rdv.dateHeure),
                                          style: TextStyle(
                                            fontSize: 11,
                                            fontWeight: FontWeight.w700,
                                            color: _statutColor(rdv.statut, context),
                                          ),
                                        ),
                                      ),
                                      title: Text(rdv.patientNom),
                                      subtitle: Text(
                                        '${rdv.numeroDossier}\nDr ${rdv.medecinNom} · ${rdv.motif}',
                                      ),
                                      isThreeLine: true,
                                      trailing: Column(
                                        mainAxisAlignment: MainAxisAlignment.center,
                                        children: [
                                          Chip(
                                            label: Text(
                                              rdv.statutLabel,
                                              style: const TextStyle(fontSize: 11),
                                            ),
                                            visualDensity: VisualDensity.compact,
                                          ),
                                          if (canManage && rdv.peutGerer)
                                            TextButton(
                                              onPressed: () => _openManage(rdv),
                                              child: const Text('Gérer'),
                                            )
                                          else
                                            TextButton(
                                              onPressed: () => _openManage(rdv),
                                              child: const Text('Voir'),
                                            ),
                                        ],
                                      ),
                                    ),
                                  );
                                },
                              ),
                  ),
          ),
        ],
      ),
    );
  }
}
