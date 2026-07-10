import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/staff_models.dart';
import '../services/patient_services.dart';
import '../services/staff_services.dart';
import 'login_screen.dart';
import 'staff_rendez_vous_screen.dart';

class StaffHomeScreen extends StatefulWidget {
  const StaffHomeScreen({super.key});

  static const route = '/staff-home';

  @override
  State<StaffHomeScreen> createState() => _StaffHomeScreenState();
}

class _StaffHomeScreenState extends State<StaffHomeScreen> {
  RdvStats? _stats;
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
      final stats = await context.read<RendezVousStaffService>().fetchStats();
      if (mounted) setState(() => _stats = stats);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _logout() async {
    await context.read<AuthService>().logout();
    if (!mounted) return;
    Navigator.of(context).pushReplacementNamed(LoginScreen.route);
  }

  String _roleLabel(String role) {
    switch (role) {
      case 'admin':
        return 'Administrateur';
      case 'medecin':
        return 'Médecin';
      case 'infirmier':
        return 'Infirmier(ère)';
      case 'comptable':
        return 'Comptable';
      default:
        return role;
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthService>();
    final user = auth.user;

    return Scaffold(
      appBar: AppBar(
        title: const Text('SGHL Staff'),
        actions: [
          IconButton(onPressed: _load, icon: const Icon(Icons.refresh)),
          IconButton(onPressed: _logout, icon: const Icon(Icons.logout)),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _load,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  if (user != null)
                    Card(
                      child: ListTile(
                        leading: CircleAvatar(
                          child: Text(
                            user.firstName.isNotEmpty
                                ? user.firstName[0].toUpperCase()
                                : user.username[0].toUpperCase(),
                          ),
                        ),
                        title: Text(user.fullName.isNotEmpty ? user.fullName : user.username),
                        subtitle: Text(_roleLabel(user.role)),
                      ),
                    ),
                  const SizedBox(height: 16),
                  if (_error != null) ...[
                    Text(_error!, textAlign: TextAlign.center),
                    const SizedBox(height: 12),
                    Center(child: FilledButton(onPressed: _load, child: const Text('Réessayer'))),
                  ],
                  if (_stats != null) ...[
                    Row(
                      children: [
                        Expanded(
                          child: _KpiCard(
                            label: 'Aujourd\'hui',
                            value: '${_stats!.rdvAujourdhui}',
                            color: Theme.of(context).colorScheme.primaryContainer,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: _KpiCard(
                            label: 'À venir',
                            value: '${_stats!.rdvPlanifies}',
                            color: Theme.of(context).colorScheme.secondaryContainer,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),
                  ],
                  Card(
                    clipBehavior: Clip.antiAlias,
                    child: InkWell(
                      onTap: () => Navigator.pushNamed(context, StaffRendezVousScreen.route),
                      child: Padding(
                        padding: const EdgeInsets.all(20),
                        child: Row(
                          children: [
                            Icon(
                              Icons.event_note_outlined,
                              size: 40,
                              color: Theme.of(context).colorScheme.primary,
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'Rendez-vous',
                                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                          fontWeight: FontWeight.w700,
                                        ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    auth.canManageRdv
                                        ? 'Consulter, confirmer, reporter ou annuler'
                                        : 'Consultation du planning (lecture seule)',
                                    style: Theme.of(context).textTheme.bodySmall,
                                  ),
                                ],
                              ),
                            ),
                            const Icon(Icons.chevron_right),
                          ],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Interface web complète recommandée pour la facturation, la pharmacie et les autres modules.',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ),
    );
  }
}

class _KpiCard extends StatelessWidget {
  const _KpiCard({required this.label, required this.value, required this.color});

  final String label;
  final String value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: color,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: Theme.of(context).textTheme.bodySmall),
            const SizedBox(height: 4),
            Text(
              value,
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
            ),
          ],
        ),
      ),
    );
  }
}
