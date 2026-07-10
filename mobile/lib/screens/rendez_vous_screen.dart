import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../models/patient_models.dart';
import '../services/patient_services.dart';

class RendezVousScreen extends StatefulWidget {
  const RendezVousScreen({super.key});

  static const route = '/rendez-vous';

  @override
  State<RendezVousScreen> createState() => _RendezVousScreenState();
}

class _RendezVousScreenState extends State<RendezVousScreen> {
  List<RendezVousPatient> _items = [];
  List<MedecinDispo> _medecins = [];
  bool _loading = true;
  bool _saving = false;
  String? _error;

  int? _medecinId;
  DateTime? _dateHeure;
  final _motifController = TextEditingController();
  final _emailController = TextEditingController();
  final _emailConfirmController = TextEditingController();
  final _telephoneController = TextEditingController();
  final _adresseController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _motifController.dispose();
    _emailController.dispose();
    _emailConfirmController.dispose();
    _telephoneController.dispose();
    _adresseController.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final service = context.read<PatientService>();
      final results = await Future.wait([
        service.fetchRendezVous(),
        service.fetchMedecins(),
      ]);
      if (mounted) {
        setState(() {
          _items = results[0] as List<RendezVousPatient>;
          _medecins = results[1] as List<MedecinDispo>;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
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

  Future<void> _pickDateTime() async {
    final now = DateTime.now();
    final date = await showDatePicker(
      context: context,
      initialDate: _dateHeure ?? now.add(const Duration(days: 1)),
      firstDate: now,
      lastDate: now.add(const Duration(days: 90)),
      locale: const Locale('fr', 'FR'),
    );
    if (date == null || !mounted) return;

    final time = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.fromDateTime(
        _dateHeure ?? now.add(const Duration(hours: 1)),
      ),
    );
    if (time == null || !mounted) return;

    setState(() {
      _dateHeure = DateTime(
        date.year,
        date.month,
        date.day,
        time.hour,
        time.minute,
      );
    });
  }

  Future<void> _createRdv() async {
    if (_medecinId == null ||
        _dateHeure == null ||
        _motifController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Renseignez médecin, date et motif.')),
      );
      return;
    }
    final email = _emailController.text.trim();
    final emailConfirm = _emailConfirmController.text.trim();
    final telephone = _telephoneController.text.trim();
    if (email.isEmpty || emailConfirm.isEmpty || telephone.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('E-mail (×2) et téléphone sont obligatoires.'),
        ),
      );
      return;
    }
    if (email.toLowerCase() != emailConfirm.toLowerCase()) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Les adresses e-mail ne correspondent pas.'),
        ),
      );
      return;
    }

    setState(() => _saving = true);
    try {
      await context.read<PatientService>().creerRendezVous(
        medecinId: _medecinId!,
        dateHeure: _dateHeure!,
        motif: _motifController.text.trim(),
        email: email,
        emailConfirm: emailConfirm,
        telephone: telephone,
        adresse: _adresseController.text.trim(),
      );
      if (!mounted) return;
      _motifController.clear();
      setState(() {
        _medecinId = null;
        _dateHeure = null;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Demande enregistrée — e-mail de confirmation si adresse renseignée.',
          ),
        ),
      );
      await _load();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(e.toString())));
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  Future<void> _annuler(RendezVousPatient rdv) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Annuler le rendez-vous ?'),
        content: Text('${_formatDate(rdv.dateHeure)} — ${rdv.medecinNom}'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Non'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Oui'),
          ),
        ],
      ),
    );
    if (ok != true || !mounted) return;

    try {
      await context.read<PatientService>().annulerRendezVous(
        rdvId: rdv.id,
        version: rdv.version,
        motifAnnulation: 'Annulation patient',
      );
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Rendez-vous annulé.')));
      await _load();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(e.toString())));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Mes rendez-vous')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _loading ? null : () => _showCreateSheet(context),
        icon: const Icon(Icons.add),
        label: const Text('Prendre RDV'),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _load,
              child: _error != null
                  ? ListView(
                      children: [
                        const SizedBox(height: 120),
                        Center(
                          child: Text(_error!, textAlign: TextAlign.center),
                        ),
                        const SizedBox(height: 12),
                        Center(
                          child: FilledButton(
                            onPressed: _load,
                            child: const Text('Réessayer'),
                          ),
                        ),
                      ],
                    )
                  : _items.isEmpty
                  ? ListView(
                      children: const [
                        SizedBox(height: 120),
                        Center(child: Text('Aucun rendez-vous')),
                      ],
                    )
                  : ListView.separated(
                      padding: const EdgeInsets.all(16),
                      itemCount: _items.length,
                      separatorBuilder: (context, index) =>
                          const SizedBox(height: 8),
                      itemBuilder: (context, index) {
                        final rdv = _items[index];
                        return Card(
                          child: Padding(
                            padding: const EdgeInsets.all(12),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Container(
                                  padding: const EdgeInsets.all(10),
                                  decoration: BoxDecoration(
                                    color: Theme.of(
                                      context,
                                    ).colorScheme.primaryContainer,
                                    borderRadius: BorderRadius.circular(10),
                                  ),
                                  child: const Icon(Icons.event_outlined),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Row(
                                        children: [
                                          Expanded(
                                            child: Text(
                                              rdv.medecinNom,
                                              style: Theme.of(
                                                context,
                                              ).textTheme.titleMedium,
                                            ),
                                          ),
                                          Chip(label: Text(rdv.statutLabel)),
                                        ],
                                      ),
                                      const SizedBox(height: 6),
                                      Text(_formatDate(rdv.dateHeure)),
                                      const SizedBox(height: 4),
                                      Text(rdv.motif),
                                      const SizedBox(height: 8),
                                      if (rdv.peutAnnuler)
                                        Align(
                                          alignment: Alignment.centerRight,
                                          child: TextButton(
                                            onPressed: () => _annuler(rdv),
                                            child: const Text('Annuler'),
                                          ),
                                        ),
                                    ],
                                  ),
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

  Future<void> _prefillProfil() async {
    try {
      final profil = await context.read<PatientService>().fetchProfil();
      if (profil.email.isNotEmpty && _emailController.text.isEmpty) {
        _emailController.text = profil.email;
        _emailConfirmController.text = profil.email;
      }
      if (profil.telephone.isNotEmpty && _telephoneController.text.isEmpty) {
        _telephoneController.text = profil.telephone;
      }
      if (profil.adresse.isNotEmpty && _adresseController.text.isEmpty) {
        _adresseController.text = profil.adresse;
      }
    } catch (_) {}
  }

  Future<void> _showCreateSheet(BuildContext context) async {
    await _prefillProfil();
    if (!context.mounted) return;
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (ctx) {
        return DraggableScrollableSheet(
          initialChildSize: 0.9,
          minChildSize: 0.5,
          maxChildSize: 0.95,
          expand: false,
          builder: (context, scrollController) {
            return Padding(
              padding: EdgeInsets.only(
                left: 16,
                right: 16,
                top: 16,
                bottom: MediaQuery.of(ctx).viewInsets.bottom + 16,
              ),
              child: ListView(
                controller: scrollController,
                children: [
                  Text(
                    'Nouveau rendez-vous',
                    style: Theme.of(ctx).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Vos coordonnées servent aux confirmations et rappels par e-mail.',
                    style: Theme.of(ctx).textTheme.bodySmall,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Coordonnées',
                    style: Theme.of(ctx).textTheme.titleSmall,
                  ),
                  const SizedBox(height: 8),
                  TextField(
                    controller: _emailController,
                    decoration: const InputDecoration(
                      labelText: 'E-mail *',
                      hintText: 'vous@exemple.com',
                    ),
                    keyboardType: TextInputType.emailAddress,
                    autocorrect: false,
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _emailConfirmController,
                    decoration: const InputDecoration(
                      labelText: 'Confirmer l\'e-mail *',
                    ),
                    keyboardType: TextInputType.emailAddress,
                    autocorrect: false,
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _telephoneController,
                    decoration: const InputDecoration(
                      labelText: 'Téléphone *',
                      hintText: '+242 06 000 00 00',
                    ),
                    keyboardType: TextInputType.phone,
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _adresseController,
                    decoration: const InputDecoration(
                      labelText: 'Adresse postale',
                    ),
                    maxLines: 2,
                  ),
                  const SizedBox(height: 20),
                  Text(
                    'Consultation',
                    style: Theme.of(ctx).textTheme.titleSmall,
                  ),
                  const SizedBox(height: 8),
                  DropdownButtonFormField<int>(
                    initialValue: _medecinId,
                    decoration: const InputDecoration(labelText: 'Médecin *'),
                    items: _medecins
                        .map(
                          (m) =>
                              DropdownMenuItem(value: m.id, child: Text(m.nom)),
                        )
                        .toList(),
                    onChanged: (v) => setState(() => _medecinId = v),
                  ),
                  const SizedBox(height: 12),
                  OutlinedButton.icon(
                    onPressed: _pickDateTime,
                    icon: const Icon(Icons.calendar_today_outlined),
                    label: Text(
                      _dateHeure == null
                          ? 'Choisir date et heure *'
                          : _formatDate(_dateHeure!.toIso8601String()),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _motifController,
                    decoration: const InputDecoration(labelText: 'Motif *'),
                    maxLines: 2,
                  ),
                  const SizedBox(height: 20),
                  FilledButton(
                    onPressed: _saving
                        ? null
                        : () async {
                            Navigator.pop(ctx);
                            await _createRdv();
                          },
                    child: _saving
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Text('Demander le rendez-vous'),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }
}
