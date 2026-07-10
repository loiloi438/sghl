import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/theme_notifier.dart';
import '../services/patient_services.dart';
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

  void _fillDemoPatient() {
    _usernameController.text = 'patient';
    _passwordController.text = 'Patient@SGHL2026';
  }

  void _fillDemoMedecin() {
    _usernameController.text = 'medecin';
    _passwordController.text = 'Medecin@SGHL2026';
  }

  Future<void> _submitLogin() async {
    if (!_formKey.currentState!.validate()) return;

    final auth = context.read<AuthService>();
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
    final themeNotifier = context.watch<ThemeNotifier>();

    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(20, 16, 20, 32),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'SGHL',
                            style: TextStyle(
                              fontSize: 22,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                          Text('Portail patient & staff mobile'),
                        ],
                      ),
                    ),
                    IconButton(
                      onPressed: () => context.read<ThemeNotifier>().toggle(),
                      icon: Icon(
                        themeNotifier.isDark
                            ? Icons.light_mode_outlined
                            : Icons.dark_mode_outlined,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                Text(
                  _mode == _AuthMode.mfa ? 'Vérification MFA' : 'Connexion',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
                const SizedBox(height: 8),
                Text(
                  _mode == _AuthMode.mfa
                      ? 'Code reçu par e-mail (personnel hospitalier).'
                      : 'Patient ou personnel autorisé (médecin, infirmier…).',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Theme.of(context).colorScheme.outline,
                      ),
                ),
                const SizedBox(height: 20),
                if (_infoMessage != null) ...[
                  _MessageBanner(text: _infoMessage!, success: true),
                  const SizedBox(height: 12),
                ],
                if (auth.error != null) ...[
                  _MessageBanner(text: auth.error!, success: false),
                  const SizedBox(height: 12),
                ],
                if (_mode == _AuthMode.login) ...[
                  TextFormField(
                    controller: _usernameController,
                    decoration: const InputDecoration(labelText: 'Identifiant'),
                    validator: (v) =>
                        (v == null || v.isEmpty) ? 'Identifiant requis' : null,
                  ),
                  const SizedBox(height: 12),
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
                  const SizedBox(height: 20),
                  FilledButton(
                    onPressed: auth.loading ? null : _submitLogin,
                    child: Text(auth.loading ? 'Connexion…' : 'Se connecter'),
                  ),
                  const SizedBox(height: 12),
                  OutlinedButton(
                    onPressed: () =>
                        Navigator.pushNamed(context, RegisterScreen.route),
                    child: const Text('Créer un compte patient'),
                  ),
                  const SizedBox(height: 16),
                  _DemoAccounts(
                    onPatient: _fillDemoPatient,
                    onMedecin: _fillDemoMedecin,
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
                  FilledButton(
                    onPressed: auth.loading ? null : _submitMfa,
                    child: Text(auth.loading ? 'Vérification…' : 'Valider le code'),
                  ),
                  const SizedBox(height: 8),
                  TextButton(onPressed: _resendMfa, child: const Text('Renvoyer le code')),
                  TextButton(onPressed: _backToLogin, child: const Text('← Retour')),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _MessageBanner extends StatelessWidget {
  const _MessageBanner({required this.text, required this.success});

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

class _DemoAccounts extends StatelessWidget {
  const _DemoAccounts({required this.onPatient, required this.onMedecin});

  final VoidCallback onPatient;
  final VoidCallback onMedecin;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Comptes démo',
              style: Theme.of(context).textTheme.labelLarge,
            ),
            const SizedBox(height: 8),
            ListTile(
              dense: true,
              title: const Text('Patient'),
              subtitle: const Text('patient / Patient@SGHL2026'),
              onTap: onPatient,
            ),
            ListTile(
              dense: true,
              title: const Text('Médecin (MFA e-mail)'),
              subtitle: const Text('medecin / Medecin@SGHL2026'),
              onTap: onMedecin,
            ),
          ],
        ),
      ),
    );
  }
}
