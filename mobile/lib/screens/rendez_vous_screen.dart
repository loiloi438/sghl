import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';

import '../core/api_config.dart';
import '../core/api_errors.dart';
import '../core/sghl_theme.dart';
import '../models/patient_models.dart';
import '../services/patient_services.dart';
import '../widgets/sghl_design_system.dart';
import '../widgets/human_care_widgets.dart';

class RendezVousScreen extends StatefulWidget {
  const RendezVousScreen({super.key, this.embedded = false});

  static const route = '/rendez-vous';

  final bool embedded;

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
  String _typeConsultation = 'presentiel';
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
    final service = context.read<PatientService>();
    try {
      final items = await service.fetchRendezVous();
      if (mounted) setState(() => _items = items);
    } catch (e) {
      if (mounted) setState(() => _error = friendlyApiError(e));
    }
    try {
      final medecins = await service.fetchMedecins();
      if (mounted) setState(() => _medecins = medecins);
    } catch (_) {
      // La liste des médecins est chargée à la demande pour la prise de RDV.
    }
    if (mounted) setState(() => _loading = false);
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
    final isTeleconsultation = _typeConsultation == 'teleconsultation';
    try {
      await context.read<PatientService>().creerRendezVous(
        medecinId: _medecinId!,
        dateHeure: _dateHeure!,
        motif: _motifController.text.trim(),
        email: email,
        emailConfirm: emailConfirm,
        telephone: telephone,
        adresse: _adresseController.text.trim(),
        typeConsultation: _typeConsultation,
      );
      if (!mounted) return;
      _motifController.clear();
      setState(() {
        _medecinId = null;
        _dateHeure = null;
        _typeConsultation = 'presentiel';
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            isTeleconsultation
                ? 'Rendez-vous planifié ✅ Lien visio après validation.'
                : 'Rendez-vous planifié ✅ Le secrétariat vous confirmera bientôt.',
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

  Future<void> _openVisio(RendezVousPatient rdv) async {
    if (!rdv.hasVisioLink) return;
    final url = ApiConfig.resolvePublicWebUrl(rdv.lienVisio!.trim());
    final uri = Uri.tryParse(url);
    if (uri == null) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Lien visio invalide.')),
      );
      return;
    }
    if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Impossible d\'ouvrir la salle visio.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final bottomPad =
        widget.embedded ? kPatientShellBottomPadding : 16.0;

    return Scaffold(
      appBar: widget.embedded
          ? null
          : AppBar(
              title: const Text('Mes rendez-vous'),
              leading: const BackButton(),
            ),
      floatingActionButton: null,
      bottomNavigationBar: widget.embedded
          ? null
          : Padding(
              padding: const EdgeInsets.fromLTRB(24, 0, 24, 24),
              child: SghlHumanCareButton(
                label: 'Prendre rendez-vous',
                icon: Icons.calendar_month_rounded,
                compact: true,
                onPressed:
                    _loading ? null : () => _showCreateSheet(context),
              ),
            ),
      body: SghlHumanCareBackground(
        child: Stack(
          children: [
            _loading
              ? const Center(child: CircularProgressIndicator())
              : RefreshIndicator(
                  onRefresh: _load,
                  child: _error != null
                      ? ListView(
                          padding: EdgeInsets.fromLTRB(16, 16, 16, bottomPad),
                          children: [
                            if (widget.embedded) _EmbeddedHeader(),
                            SghlFeedbackBanner(
                              message: _error!,
                              type: SghlFeedbackType.error,
                            ),
                            const SizedBox(height: 16),
                            SghlGradientButton(
                              label: 'Réessayer',
                              onPressed: _load,
                            ),
                            const SizedBox(height: 32),
                            const SghlMedicalEmptyIllustration(),
                          ],
                        )
                      : _items.isEmpty
                          ? ListView(
                              padding:
                                  EdgeInsets.fromLTRB(16, 16, 16, bottomPad),
                              children: [
                                if (widget.embedded) const _EmbeddedHeader(),
                                const SizedBox(height: 16),
                                const SghlEmptyState(
                                  icon: Icons.calendar_month_outlined,
                                  message: 'Aucun rendez-vous pour l\'instant',
                                  subtitle:
                                      'Prenez rendez-vous en quelques clics — nous vous accompagnons 💙',
                                ),
                                const SizedBox(height: 16),
                                const SghlMedicalEmptyIllustration(),
                              ],
                            )
                          : ListView.separated(
                              padding: EdgeInsets.fromLTRB(
                                16,
                                widget.embedded ? 8 : 16,
                                16,
                                bottomPad + 72,
                              ),
                              itemCount:
                                  _items.length + (widget.embedded ? 1 : 0),
                              separatorBuilder: (context, index) =>
                                  const SizedBox(height: 10),
                              itemBuilder: (context, index) {
                                if (widget.embedded && index == 0) {
                                  return const _EmbeddedHeader();
                                }
                                final rdv = _items[
                                    widget.embedded ? index - 1 : index];
                                return SghlCard(
                                  lightSurface: true,
                                  padding: const EdgeInsets.all(14),
                                  child: Row(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Container(
                                        padding: const EdgeInsets.all(10),
                                        decoration: BoxDecoration(
                                          color: SghlColors.humanCareSky,
                                          borderRadius:
                                              BorderRadius.circular(12),
                                        ),
                                        child: const Icon(
                                          Icons.event_rounded,
                                          color: SghlColors.humanCareTeal,
                                        ),
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
                                                    style: Theme.of(context)
                                                        .textTheme
                                                        .titleMedium
                                                        ?.copyWith(
                                                          fontWeight:
                                                              FontWeight.w700,
                                                        ),
                                                  ),
                                                ),
                                                if (rdv.isTeleconsultation)
                                                  Padding(
                                                    padding:
                                                        const EdgeInsets.only(
                                                      right: 6,
                                                    ),
                                                    child: Chip(
                                                      label: const Text('Visio'),
                                                      visualDensity:
                                                          VisualDensity.compact,
                                                      backgroundColor: SghlColors
                                                          .medicalBlue
                                                          .withValues(
                                                        alpha: 0.12,
                                                      ),
                                                    ),
                                                  ),
                                                Chip(
                                                  label: Text(rdv.statutLabel),
                                                ),
                                              ],
                                            ),
                                            const SizedBox(height: 6),
                                            Text(_formatDate(rdv.dateHeure)),
                                            const SizedBox(height: 4),
                                            Text(rdv.motif),
                                            if (rdv.hasVisioLink &&
                                                rdv.peutAnnuler) ...[
                                              const SizedBox(height: 10),
                                              Align(
                                                alignment:
                                                    Alignment.centerLeft,
                                                child: FilledButton.tonalIcon(
                                                  onPressed: () =>
                                                      _openVisio(rdv),
                                                  icon: const Icon(
                                                    Icons
                                                        .videocam_rounded,
                                                    size: 18,
                                                  ),
                                                  label: const Text(
                                                    'Rejoindre la visio',
                                                  ),
                                                ),
                                              ),
                                            ],
                                            if (rdv.peutAnnuler) ...[
                                              const SizedBox(height: 8),
                                              Align(
                                                alignment:
                                                    Alignment.centerRight,
                                                child: TextButton(
                                                  onPressed: () =>
                                                      _annuler(rdv),
                                                  child:
                                                      const Text('Annuler'),
                                                ),
                                              ),
                                            ],
                                          ],
                                        ),
                                      ),
                                    ],
                                  ),
                                );
                              },
                            ),
                ),
          if (widget.embedded)
            Positioned(
              left: 0,
              right: 0,
              bottom: kPatientShellBottomPadding - 8,
              child: Center(
                child: SghlHumanCareButton(
                  label: 'Prendre rendez-vous',
                  icon: Icons.calendar_month_rounded,
                  compact: true,
                  onPressed:
                      _loading ? null : () => _showCreateSheet(context),
                ),
              ),
            ),
        ],
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
                  DropdownButtonFormField<String>(
                    initialValue: _typeConsultation,
                    decoration: const InputDecoration(
                      labelText: 'Type de consultation',
                    ),
                    items: const [
                      DropdownMenuItem(
                        value: 'presentiel',
                        child: Text('Présentiel'),
                      ),
                      DropdownMenuItem(
                        value: 'teleconsultation',
                        child: Text('Téléconsultation (visio)'),
                      ),
                    ],
                    onChanged: (v) {
                      if (v != null) setState(() => _typeConsultation = v);
                    },
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _motifController,
                    decoration: const InputDecoration(labelText: 'Motif *'),
                    maxLines: 2,
                  ),
                  const SizedBox(height: 20),
                  SghlHumanCareButton(
                    label: 'Demander le rendez-vous',
                    icon: Icons.send_rounded,
                    onPressed: _saving
                        ? null
                        : () async {
                            Navigator.pop(ctx);
                            await _createRdv();
                          },
                    loading: _saving,
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

class _EmbeddedHeader extends StatelessWidget {
  const _EmbeddedHeader();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 48, bottom: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '🌿 Human-Care',
            style: Theme.of(context).textTheme.labelLarge,
          ),
          const SizedBox(height: 4),
          Text(
            'Mes rendez-vous',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.w800,
                ),
          ),
          const SizedBox(height: 4),
          Text(
            'Confirmations et rappels par e-mail 💙',
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
      ),
    );
  }
}
