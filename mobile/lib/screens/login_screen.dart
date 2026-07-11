import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/api_config.dart';
import '../core/sghl_theme.dart';
import '../core/theme_notifier.dart';
import '../services/patient_services.dart';
import '../widgets/sghl_design_system.dart';
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
  final _serverController = TextEditingController();
  bool _showPassword = false;
  bool _showServerSettings = false;
  _AuthMode _mode = _AuthMode.login;
  String? _infoMessage;

  @override
  void initState() {
    super.initState();
    if (!ApiConfig.usesLocalDefault) {
      _serverController.text = ApiConfig.baseUrl;
    }
    _showServerSettings = ApiConfig.usesLocalDefault;
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    _mfaController.dispose();
    _serverController.dispose();
    super.dispose();
  }

  Future<bool> _persistServerUrl() async {
    final raw = _serverController.text.trim();
    if (raw.isEmpty) {
      setState(() => _infoMessage = null);
      if (ApiConfig.usesLocalDefault) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              'Indiquez l\'adresse du serveur SGHL (ex. http://192.168.1.10:8000/api/v1).',
            ),
          ),
        );
        return false;
      }
      return true;
    }

    final uri = Uri.tryParse(raw);
    if (uri == null ||
        !uri.hasScheme ||
        (uri.scheme != 'http' && uri.scheme != 'https') ||
        uri.host.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('URL serveur invalide. Exemple : http://192.168.1.10:8000/api/v1'),
        ),
      );
      return false;
    }

    await ApiConfig.setBaseUrl(raw);
    return true;
  }

  Future<void> _submitLogin() async {
    if (!_formKey.currentState!.validate()) return;
    if (!await _persistServerUrl()) return;

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
      body: SghlLoginBackground(
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(24, 20, 24, 32),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'SGHL',
                              style: SghlTypography.montserrat(
                                fontSize: SghlTypography.display,
                                fontWeight: FontWeight.w800,
                                color: SghlColors.textLight,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Portail patient & staff mobile',
                              style: SghlTypography.montserrat(
                                fontSize: SghlTypography.label,
                                fontWeight: FontWeight.w500,
                                color: SghlColors.mutedLight,
                              ),
                            ),
                          ],
                        ),
                      ),
                      IconButton(
                        onPressed: () => context.read<ThemeNotifier>().toggle(),
                        icon: Icon(
                          themeNotifier.isDark
                              ? Icons.light_mode_outlined
                              : Icons.dark_mode_outlined,
                          color: SghlColors.mutedLight,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 32),
                  if (_mode == _AuthMode.login) ...[
                    Text(
                      'Connexion',
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            fontWeight: FontWeight.w800,
                          ),
                    ),
                    const SizedBox(height: 20),
                  ],
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
                    _ServerSettings(
                      expanded: _showServerSettings,
                      controller: _serverController,
                      onToggle: () =>
                          setState(() => _showServerSettings = !_showServerSettings),
                    ),
                    const SizedBox(height: 24),
                    SghlPrimaryButton(
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
                    Text(
                      'Vérification MFA',
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            fontWeight: FontWeight.w800,
                          ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Code reçu par e-mail (personnel hospitalier).',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                    const SizedBox(height: 20),
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
                    SghlPrimaryButton(
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
    );
  }
}

class _ServerSettings extends StatelessWidget {
  const _ServerSettings({
    required this.expanded,
    required this.controller,
    required this.onToggle,
  });

  final bool expanded;
  final TextEditingController controller;
  final VoidCallback onToggle;

  @override
  Widget build(BuildContext context) {
    return SghlCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          InkWell(
            onTap: onToggle,
            borderRadius: BorderRadius.circular(8),
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Row(
                children: [
                  Icon(
                    expanded ? Icons.expand_less : Icons.expand_more,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Serveur SGHL',
                      style: Theme.of(context).textTheme.labelLarge?.copyWith(
                            fontWeight: FontWeight.w700,
                          ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          if (expanded) ...[
            const SizedBox(height: 8),
            Text(
              'Sur téléphone, indiquez l\'adresse IP de votre serveur (même réseau Wi‑Fi).',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 10),
            TextFormField(
              controller: controller,
              keyboardType: TextInputType.url,
              decoration: const InputDecoration(
                labelText: 'URL de l\'API',
                hintText: 'http://192.168.1.10:8000/api/v1',
              ),
            ),
          ],
        ],
      ),
    );
  }
}
