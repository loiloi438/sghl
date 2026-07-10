import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/api_errors.dart';
import '../services/patient_services.dart';
import '../widgets/sghl_design_system.dart';
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
      appBar: AppBar(
        title: const Text('Validation du compte'),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      extendBodyBehindAppBar: true,
      body: SghlLoginBackground(
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: SghlCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    'Activez votre compte',
                    style: Theme.of(context)
                        .textTheme
                        .headlineSmall
                        ?.copyWith(fontWeight: FontWeight.w800),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Un code de validation a été envoyé par e-mail. Saisissez-le pour activer votre compte.',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Theme.of(context).colorScheme.outline,
                        ),
                  ),
                  const SizedBox(height: 16),
                  if (_message != null)
                    SghlFeedbackBanner(
                      message: _message!,
                      type: SghlFeedbackType.success,
                    ),
                  if (_error != null) ...[
                    const SizedBox(height: 8),
                    SghlFeedbackBanner(
                      message: _error!,
                      type: SghlFeedbackType.error,
                    ),
                  ],
                  const SizedBox(height: 16),
                  TextField(
                    controller: _usernameController,
                    decoration: const InputDecoration(
                      labelText: 'Identifiant',
                      prefixIcon: Icon(Icons.person_outline_rounded),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _codeController,
                    keyboardType: TextInputType.number,
                    maxLength: 6,
                    decoration: const InputDecoration(
                      labelText: 'Code de validation',
                      counterText: '',
                      prefixIcon: Icon(Icons.pin_outlined),
                    ),
                  ),
                  const SizedBox(height: 20),
                  SghlCoralButton(
                    label: _loading ? 'Validation…' : 'Valider',
                    loading: _loading,
                    onPressed: _validate,
                  ),
                  TextButton(
                    onPressed: _resendLoading ? null : _resend,
                    child: Text(
                      _resendLoading ? 'Envoi…' : 'Renvoyer le code',
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
