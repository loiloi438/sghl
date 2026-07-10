import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/api_errors.dart';
import '../services/patient_services.dart';
import 'login_screen.dart';

class ValidateAccountScreen extends StatefulWidget {
  const ValidateAccountScreen({super.key, this.initialUsername = ''});

  static const route = '/validate-account';

  final String initialUsername;

  @override
  State<ValidateAccountScreen> createState() => _ValidateAccountScreenState();
}

class _ValidateAccountScreenState extends State<ValidateAccountScreen> {
  late final TextEditingController _usernameController;
  final _codeController = TextEditingController();
  bool _loading = false;
  bool _resendLoading = false;
  String? _message;
  String? _error;

  @override
  void initState() {
    super.initState();
    _usernameController = TextEditingController(text: widget.initialUsername);
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _codeController.dispose();
    super.dispose();
  }

  Future<void> _validate() async {
    setState(() {
      _loading = true;
      _error = null;
      _message = null;
    });
    try {
      final detail = await context.read<PatientService>().validateAccount(
            username: _usernameController.text,
            code: _codeController.text,
          );
      if (!mounted) return;
      setState(() => _message = detail);
      await Future<void>.delayed(const Duration(milliseconds: 900));
      if (mounted) {
        Navigator.pushNamedAndRemoveUntil(
          context,
          LoginScreen.route,
          (route) => false,
        );
      }
    } catch (e) {
      if (mounted) setState(() => _error = friendlyApiError(e));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _resend() async {
    setState(() {
      _resendLoading = true;
      _error = null;
    });
    try {
      final detail = await context
          .read<PatientService>()
          .resendValidationCode(_usernameController.text);
      if (mounted) setState(() => _message = detail);
    } catch (e) {
      if (mounted) setState(() => _error = friendlyApiError(e));
    } finally {
      if (mounted) setState(() => _resendLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Validation du compte')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Un code de validation a été envoyé par e-mail. Saisissez-le pour activer votre compte.',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 16),
            if (_message != null)
              _Banner(text: _message!, success: true),
            if (_error != null) ...[
              const SizedBox(height: 8),
              _Banner(text: _error!, success: false),
            ],
            const SizedBox(height: 16),
            TextField(
              controller: _usernameController,
              decoration: const InputDecoration(labelText: 'Identifiant'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _codeController,
              keyboardType: TextInputType.number,
              maxLength: 6,
              decoration: const InputDecoration(
                labelText: 'Code de validation',
                counterText: '',
              ),
            ),
            const SizedBox(height: 20),
            FilledButton(
              onPressed: _loading ? null : _validate,
              child: Text(_loading ? 'Validation…' : 'Valider'),
            ),
            TextButton(
              onPressed: _resendLoading ? null : _resend,
              child: Text(_resendLoading ? 'Envoi…' : 'Renvoyer le code'),
            ),
          ],
        ),
      ),
    );
  }
}

class _Banner extends StatelessWidget {
  const _Banner({required this.text, required this.success});

  final String text;
  final bool success;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: success
            ? Theme.of(context).colorScheme.primaryContainer
            : Theme.of(context).colorScheme.errorContainer,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(text),
    );
  }
}
