import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/api_errors.dart';
import '../services/patient_services.dart';
import '../widgets/server_settings_card.dart';
import '../widgets/sghl_design_system.dart';
import '../widgets/human_care_widgets.dart';
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
    final serverOk =
        await _serverSettingsKey.currentState?.persistServerUrl(context) ?? false;
    if (!serverOk || !mounted) return;

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
    return Scaffold(
      appBar: AppBar(
        title: const Text('Créer un compte patient'),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      extendBodyBehindAppBar: true,
      body: SghlHumanCareBackground(
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
            child: Form(
              key: _formKey,
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
                      'Inscription patient',
                      style: Theme.of(context)
                          .textTheme
                          .headlineSmall
                          ?.copyWith(fontWeight: FontWeight.w800),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Créez votre espace patient — simple, rassurant et sécurisé 💙',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                    const SizedBox(height: 16),
                    if (_error != null) ...[
                      SghlFeedbackBanner(
                        message: _error!,
                        type: SghlFeedbackType.error,
                      ),
                      const SizedBox(height: 12),
                    ],
                    ServerSettingsCard(
                      key: _serverSettingsKey,
                      initiallyExpanded: true,
                    ),
                    const SizedBox(height: 16),
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
                      label: _loading ? 'Création…' : 'Créer mon compte patient',
                      loading: _loading,
                      onPressed: _loading ? null : _submit,
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
