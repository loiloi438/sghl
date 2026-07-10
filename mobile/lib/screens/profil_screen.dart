import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../core/api_errors.dart';
import '../models/patient_models.dart';
import '../services/patient_services.dart';
import 'login_screen.dart';

class ProfilScreen extends StatefulWidget {
  const ProfilScreen({super.key});

  static const route = '/profil';

  @override
  State<ProfilScreen> createState() => _ProfilScreenState();
}

class _ProfilScreenState extends State<ProfilScreen> {
  PatientProfil? _profil;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final profil = await context.read<PatientService>().fetchProfil();
      if (mounted) setState(() => _profil = profil);
    } catch (e) {
      if (mounted) setState(() => _error = friendlyApiError(e));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthService>();

    return Scaffold(
      appBar: AppBar(title: const Text('Mon profil')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(_error!, textAlign: TextAlign.center),
                      const SizedBox(height: 12),
                      FilledButton(onPressed: _load, child: const Text('Réessayer')),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _load,
                  child: ListView(
                    padding: const EdgeInsets.all(16),
                    children: [
                      CircleAvatar(
                        radius: 36,
                        child: Text(
                          _profil!.prenom.isNotEmpty
                              ? _profil!.prenom[0].toUpperCase()
                              : '?',
                          style: const TextStyle(fontSize: 28),
                        ),
                      ),
                      const SizedBox(height: 16),
                      Text(
                        '${_profil!.prenom} ${_profil!.nom}',
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                      const SizedBox(height: 16),
                      _InfoTile(label: 'Dossier', value: _profil!.numeroDossier),
                      _InfoTile(label: 'Date de naissance', value: _profil!.dateNaissance),
                      _InfoTile(label: 'Sexe', value: _profil!.sexe),
                      _InfoTile(label: 'Téléphone', value: _profil!.telephone),
                      _InfoTile(label: 'E-mail', value: _profil!.email),
                      _InfoTile(label: 'Adresse', value: _profil!.adresse),
                      if (auth.user != null) ...[
                        const Divider(height: 32),
                        _InfoTile(label: 'Identifiant compte', value: auth.user!.username),
                        _InfoTile(label: 'E-mail compte', value: auth.user!.email),
                      ],
                      const SizedBox(height: 24),
                      OutlinedButton.icon(
                        onPressed: () async {
                          await context.read<AuthService>().logout();
                          if (!context.mounted) return;
                          Navigator.of(context).pushNamedAndRemoveUntil(
                            LoginScreen.route,
                            (route) => false,
                          );
                        },
                        icon: const Icon(Icons.logout),
                        label: const Text('Se déconnecter'),
                      ),
                    ],
                  ),
                ),
    );
  }
}

class _InfoTile extends StatelessWidget {
  const _InfoTile({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    if (value.isEmpty) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: Theme.of(context).textTheme.labelMedium),
          const SizedBox(height: 4),
          Text(value, style: Theme.of(context).textTheme.bodyLarge),
        ],
      ),
    );
  }
}
