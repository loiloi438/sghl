import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/api_config.dart';
import '../core/sghl_theme.dart';
import '../services/patient_services.dart';
import '../widgets/human_care_auth_layout.dart';
import '../widgets/human_care_widgets.dart';
import '../widgets/server_settings_card.dart';
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
  final _serverSettingsKey = GlobalKey<ServerSettingsCardState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _mfaController = TextEditingController();
  bool _showPassword = false;
  bool _showLoginForm = false;
  _AuthMode _mode = _AuthMode.login;
  String? _infoMessage;

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    _mfaController.dispose();
    super.dispose();
  }

  Future<bool> _ensureServerUrl() async {
    if (!ApiConfig.showServerSettings) return true;
    return await _serverSettingsKey.currentState?.persistServerUrl(context) ??
        false;
  }

  Future<void> _submitLogin() async {
    if (!_formKey.currentState!.validate()) return;
    final auth = context.read<AuthService>();
    if (!await _ensureServerUrl() || !mounted) return;

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
        body: _showLoginForm ? _buildLoginForm(auth) : _buildWelcome(context),
      ),
    );
  }

  Widget _buildWelcome(BuildContext context) {
    return SghlHumanCareBackground(
      child: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(24, 28, 24, 28),
          child: ConstrainedBox(
            constraints: BoxConstraints(
              minHeight: MediaQuery.sizeOf(context).height - 80,
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                TweenAnimationBuilder<double>(
                  tween: Tween(begin: 0, end: 1),
                  duration: const Duration(milliseconds: 850),
                  curve: Curves.easeOutCubic,
                  builder: (context, value, child) => Opacity(
                    opacity: value,
                    child: Transform.translate(
                      offset: Offset(0, 14 * (1 - value)),
                      child: child,
                    ),
                  ),
                  child: const SghlHumanCareLogo(),
                ),
                const SizedBox(height: 40),
                Text(
                  'Bienvenue sur SGHL',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.displaySmall?.copyWith(
                    fontSize: 30,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Votre santé, simplement et en toute confiance',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    color: SghlColors.humanCareMuted,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 28),
                const SghlMedicalWelcomeIllustration(),
                const SizedBox(height: 30),
                SghlHumanCareButton(
                  label: 'Se connecter',
                  icon: Icons.lock_outline_rounded,
                  onPressed: () => setState(() => _showLoginForm = true),
                ),
                const SizedBox(height: 14),
                OutlinedButton.icon(
                  onPressed: () =>
                      Navigator.pushNamed(context, RegisterScreen.route),
                  icon: const Icon(Icons.person_add_alt_1_rounded),
                  label: const Text('Créer un compte'),
                  style: OutlinedButton.styleFrom(
                    minimumSize: const Size.fromHeight(56),
                    textStyle: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.verified_user_outlined,
                      size: 18,
                      color: SghlColors.humanCareTeal,
                    ),
                    SizedBox(width: 8),
                    Flexible(
                      child: Text(
                        'Des soins accessibles, proches de vous',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          color: SghlColors.humanCareText,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildLoginForm(AuthService auth) {
    return Form(
      key: _formKey,
      child: SghlHumanCareAuthLayout(
        loading: auth.loading,
        leading: IconButton.filledTonal(
          tooltip: 'Retour',
          onPressed: auth.loading
              ? null
              : () => setState(() {
                  _showLoginForm = false;
                  _mode = _AuthMode.login;
                }),
          icon: const Icon(Icons.arrow_back_rounded),
        ),
        title: _mode == _AuthMode.login
            ? 'Heureux de vous revoir'
            : 'Vérification sécurisée',
        subtitle: _mode == _AuthMode.login
            ? 'Connectez-vous à votre espace santé personnel.'
            : 'Code reçu par e-mail (personnel hospitalier).',
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (_infoMessage != null) ...[
              SghlFeedbackBanner(
                message: _infoMessage!,
                type: SghlFeedbackType.info,
                title: 'Information',
              ),
              const SizedBox(height: 12),
            ],
            if (auth.error != null) ...[
              SghlFeedbackBanner(
                message: auth.error!,
                type: SghlFeedbackType.error,
                title: 'Connexion interrompue',
              ),
              const SizedBox(height: 12),
            ],
            if (_mode == _AuthMode.login) ...[
              TextFormField(
                controller: _usernameController,
                textInputAction: TextInputAction.next,
                decoration: const InputDecoration(
                  labelText: 'Identifiant',
                  prefixIcon: Icon(Icons.person_outline_rounded),
                ),
                validator: (v) =>
                    (v == null || v.isEmpty) ? 'Identifiant requis' : null,
              ),
              const SizedBox(height: 14),
              TextFormField(
                controller: _passwordController,
                obscureText: !_showPassword,
                decoration: InputDecoration(
                  labelText: 'Mot de passe',
                  prefixIcon: const Icon(Icons.lock_outline_rounded),
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
                validator: (v) =>
                    (v == null || v.isEmpty) ? 'Mot de passe requis' : null,
                onFieldSubmitted: (_) => _submitLogin(),
              ),
              if (ApiConfig.showServerSettings) ...[
                const SizedBox(height: 16),
                ServerSettingsCard(
                  key: _serverSettingsKey,
                  initiallyExpanded: ApiConfig.usesLocalDefault,
                ),
              ],
              const SizedBox(height: 20),
              SghlHumanCareButton(
                label: 'Se connecter',
                loading: auth.loading,
                icon: Icons.lock_open_rounded,
                onPressed: auth.loading ? null : _submitLogin,
              ),
              const SizedBox(height: 12),
              OutlinedButton.icon(
                onPressed: auth.loading
                    ? null
                    : () => Navigator.pushNamed(context, RegisterScreen.route),
                icon: const Icon(Icons.person_add_alt_1_rounded),
                label: const Text('Créer un compte patient'),
              ),
            ] else ...[
              TextFormField(
                controller: _mfaController,
                keyboardType: TextInputType.number,
                maxLength: 6,
                decoration: const InputDecoration(
                  labelText: 'Code de sécurité',
                  prefixIcon: Icon(Icons.verified_user_outlined),
                  counterText: '',
                ),
                validator: (v) =>
                    (v == null || v.length != 6) ? 'Code à 6 chiffres' : null,
                onFieldSubmitted: (_) => _submitMfa(),
              ),
              const SizedBox(height: 20),
              SghlHumanCareButton(
                label: 'Valider le code',
                loading: auth.loading,
                onPressed: auth.loading ? null : _submitMfa,
              ),
              const SizedBox(height: 8),
              TextButton(
                onPressed: auth.loading ? null : _resendMfa,
                child: const Text('Renvoyer le code'),
              ),
              TextButton(
                onPressed: auth.loading ? null : _backToLogin,
                child: const Text('← Retour'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
