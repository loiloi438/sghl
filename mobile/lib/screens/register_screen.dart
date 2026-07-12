import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/api_config.dart';
import '../core/api_errors.dart';
import '../core/sghl_theme.dart';
import '../services/patient_services.dart';
import '../widgets/human_care_auth_layout.dart';
import '../widgets/human_care_widgets.dart';
import '../widgets/server_settings_card.dart';
import '../widgets/sghl_design_system.dart';
import 'validate_account_screen.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  static const route = '/register';

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _serverSettingsKey = GlobalKey<ServerSettingsCardState>();
  final _nomController = TextEditingController();
  final _prenomController = TextEditingController();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();
  final _password2Controller = TextEditingController();
  String _sexe = 'M';
  DateTime? _dateNaissance;
  bool _consent = false;
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _nomController.dispose();
    _prenomController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _passwordController.dispose();
    _password2Controller.dispose();
    super.dispose();
  }

  Future<void> _pickDate() async {
    final now = DateTime.now();
    final date = await showDatePicker(
      context: context,
      initialDate: DateTime(1990, 1, 1),
      firstDate: DateTime(1920),
      lastDate: now,
      locale: const Locale('fr', 'FR'),
    );
    if (date != null) setState(() => _dateNaissance = date);
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_dateNaissance == null) {
      setState(() => _error = 'Date de naissance requise.');
      return;
    }
    if (!_consent) {
      setState(() => _error = 'Le consentement RGPD est obligatoire.');
      return;
    }

    final service = context.read<PatientService>();
    if (ApiConfig.showServerSettings) {
      final serverOk =
          await _serverSettingsKey.currentState?.persistServerUrl(context) ??
              false;
      if (!serverOk || !mounted) return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final dob = _dateNaissance!;
      final dateStr =
          '${dob.year.toString().padLeft(4, '0')}-${dob.month.toString().padLeft(2, '0')}-${dob.day.toString().padLeft(2, '0')}';
      final result = await service.registerPatient(
        nom: _nomController.text,
        prenom: _prenomController.text,
        dateNaissance: dateStr,
        sexe: _sexe,
        email: _emailController.text,
        telephone: _phoneController.text,
        password: _passwordController.text,
        passwordConfirm: _password2Controller.text,
        consentementRgpd: _consent,
      );
      if (!mounted) return;
      Navigator.pushReplacementNamed(
        context,
        ValidateAccountScreen.route,
        arguments: {
          'username': result.username,
          if (result.devValidationCode != null) 'code': result.devValidationCode,
        },
      );
    } catch (e) {
      if (mounted) setState(() => _error = friendlyApiError(e));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Theme(
      data: SghlTheme.patientHumanCare(),
      child: Scaffold(
        body: Form(
          key: _formKey,
          child: SghlHumanCareAuthLayout(
            loading: _loading,
            title: 'Inscription patient',
            subtitle: SghlHumanCareAuthLayout.welcomeSubtitle,
            leading: IconButton(
              icon: const Icon(Icons.arrow_back_rounded),
              onPressed: _loading ? null : () => Navigator.maybePop(context),
              tooltip: 'Retour',
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (_error != null) ...[
                  SghlFeedbackBanner(
                    message: _error!,
                    type: SghlFeedbackType.error,
                    title: 'Inscription interrompue',
                  ),
                  const SizedBox(height: 12),
                ],
                if (ApiConfig.showServerSettings) ...[
                  ServerSettingsCard(
                    key: _serverSettingsKey,
                    initiallyExpanded: ApiConfig.usesLocalDefault,
                  ),
                  const SizedBox(height: 16),
                ],
                    TextFormField(
                      controller: _nomController,
                      decoration: const InputDecoration(
                        labelText: 'Nom',
                        prefixIcon: Icon(Icons.badge_outlined),
                      ),
                      validator: (v) =>
                          (v == null || v.trim().isEmpty) ? 'Requis' : null,
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _prenomController,
                      decoration: const InputDecoration(
                        labelText: 'Prénom',
                        prefixIcon: Icon(Icons.person_outline_rounded),
                      ),
                      validator: (v) =>
                          (v == null || v.trim().isEmpty) ? 'Requis' : null,
                    ),
                    const SizedBox(height: 12),
                    InkWell(
                      onTap: _pickDate,
                      borderRadius: BorderRadius.circular(16),
                      child: InputDecorator(
                        decoration: const InputDecoration(
                          labelText: 'Date de naissance',
                          prefixIcon: Icon(Icons.calendar_today_rounded),
                        ),
                        child: Text(
                          _dateNaissance == null
                              ? 'Sélectionner une date'
                              : '${_dateNaissance!.day}/${_dateNaissance!.month}/${_dateNaissance!.year}',
                        ),
                      ),
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<String>(
                      initialValue: _sexe,
                      decoration: const InputDecoration(
                        labelText: 'Sexe',
                        prefixIcon: Icon(Icons.wc_outlined),
                      ),
                      items: const [
                        DropdownMenuItem(value: 'M', child: Text('Masculin')),
                        DropdownMenuItem(value: 'F', child: Text('Féminin')),
                        DropdownMenuItem(value: 'A', child: Text('Autre')),
                      ],
                      onChanged: (v) {
                        if (v != null) setState(() => _sexe = v);
                      },
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _emailController,
                      keyboardType: TextInputType.emailAddress,
                      decoration: const InputDecoration(
                        labelText: 'E-mail',
                        prefixIcon: Icon(Icons.email_outlined),
                        helperText:
                            'Un code de validation sera envoyé à cette adresse.',
                      ),
                      validator: (v) => (v == null || !v.contains('@'))
                          ? 'E-mail invalide'
                          : null,
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _phoneController,
                      keyboardType: TextInputType.phone,
                      decoration: const InputDecoration(
                        labelText: 'Téléphone',
                        prefixIcon: Icon(Icons.phone_outlined),
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _passwordController,
                      obscureText: true,
                      decoration: const InputDecoration(
                        labelText: 'Mot de passe',
                        prefixIcon: Icon(Icons.lock_outline_rounded),
                      ),
                      validator: (v) => (v == null || v.length < 8)
                          ? '8 caractères minimum'
                          : null,
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _password2Controller,
                      obscureText: true,
                      decoration: const InputDecoration(
                        labelText: 'Confirmer le mot de passe',
                        prefixIcon: Icon(Icons.lock_outline_rounded),
                      ),
                      validator: (v) => v != _passwordController.text
                          ? 'Les mots de passe ne correspondent pas'
                          : null,
                    ),
                    const SizedBox(height: 12),
                    CheckboxListTile(
                      contentPadding: EdgeInsets.zero,
                      value: _consent,
                      onChanged: (v) => setState(() => _consent = v ?? false),
                      title: const Text(
                        'J\'accepte le traitement de mes données de santé (RGPD).',
                      ),
                      controlAffinity: ListTileControlAffinity.leading,
                    ),
                    const SizedBox(height: 20),
                    SghlHumanCareButton(
                      label: 'Créer mon compte patient',
                      loading: _loading,
                      icon: Icons.person_add_alt_1_rounded,
                      onPressed: _loading ? null : _submit,
                    ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
