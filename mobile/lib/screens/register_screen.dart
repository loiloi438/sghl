import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/api_errors.dart';
import '../services/patient_services.dart';
import 'validate_account_screen.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  static const route = '/register';

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
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

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final service = context.read<PatientService>();
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
        arguments: result.username,
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
      appBar: AppBar(title: const Text('Créer un compte patient')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              if (_error != null) ...[
                _Banner(text: _error!, error: true),
                const SizedBox(height: 12),
              ],
              TextFormField(
                controller: _nomController,
                decoration: const InputDecoration(labelText: 'Nom'),
                validator: (v) => (v == null || v.trim().isEmpty) ? 'Requis' : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _prenomController,
                decoration: const InputDecoration(labelText: 'Prénom'),
                validator: (v) => (v == null || v.trim().isEmpty) ? 'Requis' : null,
              ),
              const SizedBox(height: 12),
              ListTile(
                contentPadding: EdgeInsets.zero,
                title: Text(
                  _dateNaissance == null
                      ? 'Date de naissance *'
                      : 'Né(e) le ${_dateNaissance!.day}/${_dateNaissance!.month}/${_dateNaissance!.year}',
                ),
                trailing: const Icon(Icons.calendar_today),
                onTap: _pickDate,
              ),
              DropdownButtonFormField<String>(
                value: _sexe,
                decoration: const InputDecoration(labelText: 'Sexe'),
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
                  helperText: 'Un code de validation sera envoyé à cette adresse.',
                ),
                validator: (v) =>
                    (v == null || !v.contains('@')) ? 'E-mail invalide' : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _phoneController,
                keyboardType: TextInputType.phone,
                decoration: const InputDecoration(labelText: 'Téléphone'),
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _passwordController,
                obscureText: true,
                decoration: const InputDecoration(labelText: 'Mot de passe'),
                validator: (v) =>
                    (v == null || v.length < 8) ? '8 caractères minimum' : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _password2Controller,
                obscureText: true,
                decoration: const InputDecoration(labelText: 'Confirmer le mot de passe'),
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
              FilledButton(
                onPressed: _loading ? null : _submit,
                child: Text(_loading ? 'Création…' : 'Créer mon compte'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Banner extends StatelessWidget {
  const _Banner({required this.text, this.error = false});

  final String text;
  final bool error;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: error
            ? Theme.of(context).colorScheme.errorContainer
            : Theme.of(context).colorScheme.primaryContainer,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(text),
    );
  }
}
