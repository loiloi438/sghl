import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/api_errors.dart';
import '../services/patient_services.dart';
import '../core/sghl_theme.dart';
import '../widgets/human_care_widgets.dart';
import '../widgets/sghl_design_system.dart';
import 'patient_shell.dart';

class ValidateAccountScreen extends StatefulWidget {
  const ValidateAccountScreen({
    super.key,
    this.initialUsername = '',
    this.initialCode = '',
  });

  static const route = '/validate-account';

  final String initialUsername;
  final String initialCode;

  @override
  State<ValidateAccountScreen> createState() => _ValidateAccountScreenState();
}

class _ValidateAccountScreenState extends State<ValidateAccountScreen> {
  late final TextEditingController _usernameController;
  late final TextEditingController _codeController;
  bool _loading = false;
  bool _resendLoading = false;
  String? _message;
  String? _error;

  @override
  void initState() {
    super.initState();
    _usernameController = TextEditingController(text: widget.initialUsername);
    _codeController = TextEditingController(text: widget.initialCode);
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
      final patientService = context.read<PatientService>();
      final auth = context.read<AuthService>();
      final result = await patientService.validateAccount(
            username: _usernameController.text,
            code: _codeController.text,
          );
      if (!mounted) return;
      setState(() => _message = result.detail);
      final authOk = await auth.completeValidation(
            result.accessToken,
            result.refreshToken,
          );
      if (!mounted) return;
      if (authOk) {
        Navigator.pushNamedAndRemoveUntil(
          context,
          PatientShell.route,
          (route) => false,
        );
      } else {
        setState(() => _error = auth.error);
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
    return Theme(
      data: SghlTheme.patientHumanCare(),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Validation du compte'),
          backgroundColor: Colors.transparent,
          elevation: 0,
        ),
        extendBodyBehindAppBar: true,
        body: SghlHumanCareBackground(
          child: SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: SghlCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      '🌿 Human-Care',
                      style: Theme.of(context).textTheme.labelLarge,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Activez votre compte',
                      style: Theme.of(context)
                          .textTheme
                          .headlineSmall
                          ?.copyWith(fontWeight: FontWeight.w800),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Un code de validation a été envoyé par e-mail. Saisissez-le pour accéder directement à votre espace patient 💙',
                      style: Theme.of(context).textTheme.bodyMedium,
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
                    SghlHumanCareButton(
                      label: _loading ? 'Validation…' : 'Valider et accéder à mon espace',
                      loading: _loading,
                      onPressed: _loading ? null : _validate,
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
      ),
    );
  }
}
