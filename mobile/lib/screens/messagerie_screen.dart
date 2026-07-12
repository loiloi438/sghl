import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../core/api_errors.dart';
import '../core/sghl_theme.dart';
import '../models/patient_models.dart';
import '../services/patient_services.dart';
import '../widgets/human_care_widgets.dart';
import '../widgets/patient_human_care_page.dart';
import '../widgets/sghl_design_system.dart';

class MessagerieScreen extends StatefulWidget {
  const MessagerieScreen({super.key, this.embedded = false});

  static const route = '/messagerie';

  final bool embedded;

  @override
  State<MessagerieScreen> createState() => _MessagerieScreenState();
}

class _MessagerieScreenState extends State<MessagerieScreen> {
  final _sujetController = TextEditingController();
  final _corpsController = TextEditingController();
  List<PatientMessage> _messages = [];
  bool _loading = true;
  bool _sending = false;
  String? _error;
  String? _sentOk;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _sujetController.dispose();
    _corpsController.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final data = await context.read<PatientService>().fetchMessages();
      if (mounted) setState(() => _messages = data);
    } catch (e) {
      if (mounted) setState(() => _error = friendlyApiError(e));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _send() async {
    final sujet = _sujetController.text.trim();
    final corps = _corpsController.text.trim();
    if (sujet.isEmpty || corps.isEmpty) {
      setState(() => _error = 'Sujet et message obligatoires.');
      return;
    }

    setState(() {
      _sending = true;
      _error = null;
      _sentOk = null;
    });

    try {
      await context.read<PatientService>().sendMessage(sujet: sujet, corps: corps);
      if (!mounted) return;
      _sujetController.clear();
      _corpsController.clear();
      setState(() => _sentOk = 'Message envoyé — nous vous répondrons rapidement 💙');
      await _load();
    } catch (e) {
      if (mounted) setState(() => _error = friendlyApiError(e));
    } finally {
      if (mounted) setState(() => _sending = false);
    }
  }

  String _formatDate(String iso) {
    try {
      return DateFormat('dd/MM/yyyy HH:mm').format(DateTime.parse(iso).toLocal());
    } catch (_) {
      return iso;
    }
  }

  @override
  Widget build(BuildContext context) {
    final bottomPad = widget.embedded ? kPatientShellBottomPadding : 16.0;

    return Scaffold(
      appBar: widget.embedded
          ? null
          : AppBar(
              title: const Text('Messagerie'),
              actions: [
                IconButton(
                  onPressed: _loading ? null : _load,
                  icon: const Icon(Icons.refresh_rounded),
                ),
              ],
            ),
      body: SghlHumanCareBackground(
        child: _loading && _messages.isEmpty
            ? const Center(child: CircularProgressIndicator())
            : RefreshIndicator(
                onRefresh: _load,
                color: SghlColors.humanCareTeal,
                child: ListView(
                  padding: EdgeInsets.fromLTRB(16, widget.embedded ? 8 : 16, 16, bottomPad),
                  children: [
                    PatientHcHeader(
                      title: 'Messagerie',
                      subtitle:
                          'Échangez en toute confiance avec votre médecin ou le secrétariat',
                      embedded: widget.embedded,
                      actions: widget.embedded
                          ? [
                              IconButton(
                                onPressed: _loading ? null : _load,
                                icon: const Icon(Icons.refresh_rounded),
                              ),
                            ]
                          : null,
                    ),
                    if (_error != null) ...[
                      SghlFeedbackBanner(
                        message: _error!,
                        type: SghlFeedbackType.error,
                      ),
                      const SizedBox(height: 12),
                    ],
                    if (_sentOk != null) ...[
                      SghlFeedbackBanner(
                        message: _sentOk!,
                        type: SghlFeedbackType.info,
                      ),
                      const SizedBox(height: 12),
                    ],
                    SghlCard(
                      lightSurface: true,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Text(
                            'NOUVEAU MESSAGE',
                            style: Theme.of(context).textTheme.labelSmall?.copyWith(
                                  fontWeight: FontWeight.w800,
                                  letterSpacing: 1,
                                  color: SghlColors.humanCareTeal,
                                ),
                          ),
                          const SizedBox(height: 12),
                          TextField(
                            controller: _sujetController,
                            decoration: const InputDecoration(
                              labelText: 'Sujet',
                              hintText: 'Ex. Question sur mon rendez-vous',
                            ),
                          ),
                          const SizedBox(height: 12),
                          TextField(
                            controller: _corpsController,
                            minLines: 3,
                            maxLines: 5,
                            decoration: const InputDecoration(
                              labelText: 'Message',
                              hintText: 'Décrivez votre demande…',
                              alignLabelWithHint: true,
                            ),
                          ),
                          const SizedBox(height: 16),
                          SghlHumanCareButton(
                            label: _sending ? 'Envoi…' : '✉️ Envoyer au secrétariat',
                            loading: _sending,
                            onPressed: _sending ? null : _send,
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Mes échanges',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w800,
                            color: SghlColors.humanCareText,
                          ),
                    ),
                    const SizedBox(height: 12),
                    if (_messages.isEmpty)
                      const SghlEmptyState(
                        icon: Icons.chat_bubble_outline_rounded,
                        message: 'Aucun message pour l\'instant',
                        subtitle:
                            'Vos conversations avec l\'équipe médicale s\'afficheront ici.',
                      )
                    else
                      ..._messages.map((m) => Padding(
                            padding: const EdgeInsets.only(bottom: 10),
                            child: _ChatBubble(
                              message: m,
                              formatDate: _formatDate,
                            ),
                          )),
                  ],
                ),
              ),
      ),
    );
  }
}

class _ChatBubble extends StatelessWidget {
  const _ChatBubble({required this.message, required this.formatDate});

  final PatientMessage message;
  final String Function(String) formatDate;

  @override
  Widget build(BuildContext context) {
    final incoming = message.isReceived;
    return Align(
      alignment: incoming ? Alignment.centerLeft : Alignment.centerRight,
      child: Container(
        constraints: BoxConstraints(
          maxWidth: MediaQuery.sizeOf(context).width * 0.88,
        ),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: incoming ? Colors.white : const Color(0xFFD1FAE5),
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(20),
            topRight: const Radius.circular(20),
            bottomLeft: Radius.circular(incoming ? 4 : 20),
            bottomRight: Radius.circular(incoming ? 20 : 4),
          ),
          border: Border.all(
            color: incoming ? const Color(0xFFE2E8F0) : const Color(0xFF99F6E4),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              message.sujet,
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
            ),
            const SizedBox(height: 6),
            Text(message.corps),
            const SizedBox(height: 8),
            Text(
              '${message.expediteurNom} · ${incoming ? 'Reçu' : 'Envoyé'} · ${formatDate(message.createdAt)}',
              style: Theme.of(context).textTheme.labelSmall?.copyWith(
                    color: SghlColors.humanCareMuted,
                  ),
            ),
          ],
        ),
      ),
    );
  }
}
