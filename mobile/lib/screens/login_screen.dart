import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/api_config.dart';
import '../core/sghl_theme.dart';
import '../services/patient_services.dart';
import '../widgets/server_settings_card.dart';
import '../widgets/sghl_design_system.dart';
import '../widgets/human_care_widgets.dart';
import 'patient_shell.dart';
import 'register_screen.dart';
import 'staff_home_screen.dart';

enum _AuthMode { login, mfa }

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  static const route = '/login';

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _serverSettingsKey = GlobalKey<ServerSettingsCardState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _mfaController = TextEditingController();
  bool _showPassword = false;
  _AuthMode _mode = _AuthMode.login;
  String? _infoMessage;

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    _mfaController.dispose();
    super.dispose();
  }

  Future<void> _submitLogin() async {
    if (!_formKey.currentState!.validate()) return;
    final auth = context.read<AuthService>();
    final serverOk =
        await _serverSettingsKey.currentState?.persistServerUrl(context) ?? false;
    if (!serverOk || !mounted) return;

    final result = await auth.login(
      _usernameController.text.trim(),
      _passwordController.text,
    );

    if (!mounted) return;
    if (result == LoginStatus.mfaRequired) {
      setState(() {
        _mode = _AuthMode.mfa;
        _infoMessage =
            'Un code à 6 chiffres a été envoyé par e-mail. Saisissez-le ci-dessous.';
      });
      return;
    }
    if (result == LoginStatus.success) {
      _goHome(auth);
    }
  }

  Future<void> _submitMfa() async {
    final auth = context.read<AuthService>();
    final ok = await auth.loginMfa(_mfaController.text);
    if (!mounted) return;
    if (ok) _goHome(auth);
  }

  Future<void> _resendMfa() async {
    final auth = context.read<AuthService>();
    final result = await auth.login(
      _usernameController.text.trim(),
      _passwordController.text,
    );
    if (!mounted) return;
    if (result == LoginStatus.mfaRequired) {
      setState(() => _infoMessage = 'Un nouveau code a été envoyé par e-mail.');
    }
  }

  void _goHome(AuthService auth) {
    final route = auth.isPatient ? PatientShell.route : StaffHomeScreen.route;
    Navigator.of(context).pushReplacementNamed(route);
  }

  void _backToLogin() {
    context.read<AuthService>().clearMfaPending();
    setState(() {
      _mode = _AuthMode.login;
      _mfaController.clear();
      _infoMessage = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthService>();

    return Theme(
      data: SghlTheme.patientHumanCare(),
      child: Scaffold(
        body: SghlHumanCareBackground(
          child: SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(16, 20, 16, 32),
              child: Form(
                key: _formKey,
                child: SghlCard(
                  lightSurface: true,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        '🌿 Human-Care',
                        style: Theme.of(context).textTheme.labelLarge,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        _mode == _AuthMode.login
                            ? 'Connexion patient'
                            : 'Vérification MFA',
                        style: Theme.of(context)
                            .textTheme
                            .headlineSmall
                            ?.copyWith(fontWeight: FontWeight.w800),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        _mode == _AuthMode.login
                            ? 'Accédez à votre espace santé — simple, rassurant et sécurisé 💙'
                            : 'Code reçu par e-mail (personnel hospitalier).',
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                      const SizedBox(height: 16),
                      if (_infoMessage != null) ...[
                        SghlFeedbackBanner(
                          message: _infoMessage!,
                          type: SghlFeedbackType.info,
                        ),
                        const SizedBox(height: 12),
                      ],
                      if (auth.error != null) ...[
                        SghlFeedbackBanner(
                          message: auth.error!,
                          type: SghlFeedbackType.error,
                        ),
                        const SizedBox(height: 12),
                      ],
                      if (_mode == _AuthMode.login) ...[
                        TextFormField(
                          controller: _usernameController,
                          decoration: const InputDecoration(
                            labelText: 'Identifiant',
                          ),
                          validator: (v) => (v == null || v.isEmpty)
                              ? 'Identifiant requis'
                              : null,
                        ),
                        const SizedBox(height: 14),
                        TextFormField(
                          controller: _passwordController,
                          obscureText: !_showPassword,
                          decoration: InputDecoration(
                            labelText: 'Mot de passe',
                            suffixIcon: IconButton(
                              icon: Icon(
                                _showPassword
                                    ? Icons.visibility_off_outlined
                                    : Icons.visibility_outlined,
                              ),
                              onPressed: () =>
                                  setState(() => _showPassword = !_showPassword),
                            ),
                          ),
                          validator: (v) => (v == null || v.isEmpty)
                              ? 'Mot de passe requis'
                              : null,
                          onFieldSubmitted: (_) => _submitLogin(),
                        ),
                        const SizedBox(height: 16),
                        ServerSettingsCard(
                          key: _serverSettingsKey,
                          initiallyExpanded: ApiConfig.usesLocalDefault,
                        ),
                        const SizedBox(height: 20),
                        SghlHumanCareButton(
                          label: auth.loading ? 'Connexion…' : 'Se connecter',
                          loading: auth.loading,
                          onPressed: _submitLogin,
                        ),
                        const SizedBox(height: 12),
                        OutlinedButton(
                          onPressed: () =>
                              Navigator.pushNamed(context, RegisterScreen.route),
                          child: const Text('Créer un compte patient'),
                        ),
                      ] else ...[
                        TextFormField(
                          controller: _mfaController,
                          keyboardType: TextInputType.number,
                          maxLength: 6,
                          decoration: const InputDecoration(
                            labelText: 'Code de sécurité',
                            counterText: '',
                          ),
                          validator: (v) =>
                              (v == null || v.length != 6) ? 'Code à 6 chiffres' : null,
                          onFieldSubmitted: (_) => _submitMfa(),
                        ),
                        const SizedBox(height: 20),
                        SghlHumanCareButton(
                          label: auth.loading ? 'Vérification…' : 'Valider le code',
                          loading: auth.loading,
                          onPressed: _submitMfa,
                        ),
                        const SizedBox(height: 8),
                        TextButton(
                          onPressed: _resendMfa,
                          child: const Text('Renvoyer le code'),
                        ),
                        TextButton(
                          onPressed: _backToLogin,
                          child: const Text('← Retour'),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
