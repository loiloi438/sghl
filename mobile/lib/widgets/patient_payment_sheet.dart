import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';

import '../core/api_client.dart';
import '../core/sghl_theme.dart';
import '../models/patient_models.dart';
import '../services/patient_services.dart';
import 'human_care_widgets.dart';

enum _PaymentStep { choose, pending, stripePending }

Future<bool?> showPatientPaymentSheet(
  BuildContext context, {
  required FacturePatient facture,
}) {
  return showModalBottomSheet<bool>(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    builder: (ctx) => Theme(
      data: SghlTheme.patientHumanCare(),
      child: PatientPaymentSheet(facture: facture),
    ),
  );
}

class PatientPaymentSheet extends StatefulWidget {
  const PatientPaymentSheet({super.key, required this.facture});

  final FacturePatient facture;

  @override
  State<PatientPaymentSheet> createState() => _PatientPaymentSheetState();
}

class _PatientPaymentSheetState extends State<PatientPaymentSheet> {
  static const _providers = {
    'stripe': 'Carte bancaire (Stripe)',
    'mtn': 'MTN Mobile Money',
    'airtel': 'Airtel Money',
  };

  String _provider = 'mtn';
  _PaymentStep _step = _PaymentStep.choose;
  PaiementFacture? _payment;
  bool _processing = false;
  String? _error;
  String? _message;

  String _formatMontant(String value) {
    final n = num.tryParse(value);
    if (n == null) return value;
    return NumberFormat('#,##0.00', 'fr_FR').format(n);
  }

  String _errorMessage(Object e) {
    if (e is ApiException) return e.message;
    return e.toString();
  }

  Future<void> _initiate() async {
    setState(() {
      _processing = true;
      _error = null;
      _message = null;
    });

    try {
      final service = context.read<PatientService>();
      final payment = await service.initierPaiementFacture(
        factureId: widget.facture.id,
        provider: _provider,
        version: widget.facture.version,
      );

      if (!mounted) return;
      setState(() => _payment = payment);

      if (payment.factureSettled || payment.status == 'success') {
        setState(() => _message = 'Paiement enregistré — facture soldée.');
        return;
      }

      if (payment.clientSecret != null && payment.clientSecret!.isNotEmpty) {
        setState(() => _step = _PaymentStep.stripePending);
        return;
      }

      setState(() => _step = _PaymentStep.pending);
    } catch (e) {
      if (mounted) setState(() => _error = _errorMessage(e));
    } finally {
      if (mounted) setState(() => _processing = false);
    }
  }

  Future<void> _pollStatus() async {
    final reference = _payment?.reference;
    if (reference == null || reference.isEmpty) return;

    setState(() {
      _processing = true;
      _error = null;
      _message = null;
    });

    try {
      final result =
          await context.read<PatientService>().pollPaymentStatus(reference);

      if (!mounted) return;

      if (result.status == 'success' && result.factureSettled) {
        setState(() => _message = 'Paiement confirmé — facture mise à jour.');
        return;
      }
      if (result.status == 'success' && result.settlementError != null) {
        setState(() => _error = result.settlementError);
        return;
      }
      if (result.status == 'failed') {
        setState(() => _error = 'Paiement échoué.');
        return;
      }
      setState(
        () => _message =
            'Paiement encore en attente — réessayez dans quelques instants.',
      );
    } catch (e) {
      if (mounted) setState(() => _error = _errorMessage(e));
    } finally {
      if (mounted) setState(() => _processing = false);
    }
  }

  Future<void> _openRedirect() async {
    final url = _payment?.redirectUrl;
    if (url == null || url.isEmpty) return;
    final uri = Uri.tryParse(url);
    if (uri == null) return;
    if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
      if (mounted) {
        setState(() => _error = 'Impossible d\'ouvrir la page de paiement.');
      }
    }
  }

  void _close({bool success = false}) {
    Navigator.of(context).pop(success || _message != null);
  }

  @override
  Widget build(BuildContext context) {
    final bottomInset = MediaQuery.of(context).viewInsets.bottom;

    return Padding(
      padding: EdgeInsets.fromLTRB(16, 16, 16, bottomInset + 16),
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: const Color(0xFFA7F3D0)),
        ),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                '🌿 Payer en ligne',
                style: Theme.of(context).textTheme.labelLarge,
              ),
              const SizedBox(height: 4),
              Text(
                'Facture ${widget.facture.numeroFacture ?? '—'}',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w800,
                      color: SghlColors.humanCareText,
                    ),
              ),
              const SizedBox(height: 4),
              Text(
                '${_formatMontant(widget.facture.montantRestant)} FCFA restants',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              const SizedBox(height: 16),
          if (_error != null) ...[
            _Banner(text: _error!, color: Theme.of(context).colorScheme.errorContainer),
            const SizedBox(height: 12),
          ],
          if (_message != null) ...[
            _Banner(
              text: _message!,
              color: Theme.of(context).colorScheme.primaryContainer,
            ),
            const SizedBox(height: 12),
          ],
          if (_message != null)
            SghlHumanCareButton(
              label: 'Fermer',
              onPressed: () => _close(success: true),
            )
          else if (_step == _PaymentStep.choose) ...[
            DropdownButtonFormField<String>(
              initialValue: _provider,
              decoration: const InputDecoration(labelText: 'Mode de paiement'),
              items: _providers.entries
                  .map(
                    (e) => DropdownMenuItem(value: e.key, child: Text(e.value)),
                  )
                  .toList(),
              onChanged: _processing
                  ? null
                  : (value) {
                      if (value != null) setState(() => _provider = value);
                    },
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: _processing ? null : () => _close(),
                    child: const Text('Annuler'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: SghlHumanCareButton(
                    label: _processing ? 'Initialisation…' : 'Continuer',
                    loading: _processing,
                    compact: true,
                    onPressed: _processing ? null : _initiate,
                  ),
                ),
              ],
            ),
          ] else if (_step == _PaymentStep.stripePending && _payment != null) ...[
            Text(
              'Paiement carte initié (réf. ${_payment!.reference}). '
              'La saisie carte n\'est pas encore disponible dans l\'app mobile — '
              'utilisez Mobile Money ou le portail web, puis vérifiez le statut.',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: _processing ? null : () => _close(),
                    child: const Text('Fermer'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: FilledButton(
                    onPressed: _processing ? null : _pollStatus,
                    child: Text(
                      _processing ? 'Vérification…' : 'Vérifier le paiement',
                    ),
                  ),
                ),
              ],
            ),
          ] else if (_step == _PaymentStep.pending && _payment != null) ...[
            Text(
              'Paiement Mobile Money initié (réf. ${_payment!.reference}). '
              'Confirmez la transaction sur votre téléphone, puis vérifiez le statut.',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            if (_payment!.redirectUrl != null &&
                _payment!.redirectUrl!.isNotEmpty) ...[
              const SizedBox(height: 12),
              FilledButton.tonal(
                onPressed: _openRedirect,
                child: const Text('Ouvrir la page de paiement'),
              ),
            ],
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: _processing ? null : () => _close(),
                    child: const Text('Fermer'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: FilledButton(
                    onPressed: _processing ? null : _pollStatus,
                    child: Text(
                      _processing ? 'Vérification…' : 'Vérifier le paiement',
                    ),
                  ),
                ),
              ],
            ),
          ],
            ],
          ),
        ),
      ),
    );
  }
}

class _Banner extends StatelessWidget {
  const _Banner({required this.text, required this.color});

  final String text;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Text(text),
    );
  }
}
