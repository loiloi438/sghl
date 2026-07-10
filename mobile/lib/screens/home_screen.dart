import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../core/theme_notifier.dart';
import '../models/patient_models.dart';
import '../services/notification_inbox_service.dart';
import '../services/patient_services.dart';
import 'notifications_screen.dart';
import 'constantes_screen.dart';
import 'doses_screen.dart';
import 'factures_screen.dart';
import 'laboratoire_screen.dart';
import 'login_screen.dart';
import 'plans_screen.dart';
import 'prescriptions_screen.dart';
import 'rendez_vous_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  static const route = '/home';

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  TableauBord? _dashboard;
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
      final data = await context.read<PatientService>().fetchDashboard();
      if (mounted) setState(() => _dashboard = data);
      if (mounted) {
        await context.read<NotificationInboxService>().refresh();
      }
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

  String _formatDate(String iso) {
    try {
      return DateFormat(
        'dd/MM/yyyy HH:mm',
      ).format(DateTime.parse(iso).toLocal());
    } catch (_) {
      return iso;
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthService>();
    final inbox = context.watch<NotificationInboxService>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Mon espace patient'),
        actions: [
          IconButton(
            onPressed: () =>
                Navigator.pushNamed(context, NotificationsScreen.route),
            icon: Badge(
              isLabelVisible: inbox.unreadCount > 0,
              label: Text('${inbox.unreadCount}'),
              child: const Icon(Icons.notifications_outlined),
            ),
            tooltip: 'Notifications',
          ),
          IconButton(
            onPressed: () => context.read<ThemeNotifier>().toggle(),
            icon: Icon(
              context.watch<ThemeNotifier>().isDark
                  ? Icons.light_mode_outlined
                  : Icons.dark_mode_outlined,
            ),
            tooltip: 'Thème',
          ),
          IconButton(
            onPressed: _load,
            icon: const Icon(Icons.refresh),
            tooltip: 'Actualiser',
          ),
          IconButton(
            onPressed: _logout,
            icon: const Icon(Icons.logout),
            tooltip: 'Déconnexion',
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(_error!, textAlign: TextAlign.center),
                  const SizedBox(height: 12),
                  FilledButton(
                    onPressed: _load,
                    child: const Text('Réessayer'),
                  ),
                ],
              ),
            )
          : RefreshIndicator(
              onRefresh: _load,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  _ProfilCard(
                    profil: _dashboard!.profil,
                    userName: auth.user?.fullName,
                  ),
                  const SizedBox(height: 16),
                  _SummaryCard(
                    hospitalisation: _dashboard!.hospitalisationActive,
                    nextDoseCount: _dashboard!.prochainesDoses.length,
                    recentVitalCount: _dashboard!.constantesRecentes.length,
                    formatDate: _formatDate,
                  ),
                  const SizedBox(height: 16),
                  _HospitalisationCard(
                    hospitalisation: _dashboard!.hospitalisationActive,
                    formatDate: _formatDate,
                  ),
                  const SizedBox(height: 16),
                  _SectionTitle(title: 'Raccourcis'),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      _NavChip(
                        icon: Icons.monitor_heart_outlined,
                        label: 'Constantes',
                        onTap: () => Navigator.pushNamed(
                          context,
                          ConstantesScreen.route,
                        ),
                      ),
                      _NavChip(
                        icon: Icons.medical_services_outlined,
                        label: 'Plans de soins',
                        onTap: () =>
                            Navigator.pushNamed(context, PlansScreen.route),
                      ),
                      _NavChip(
                        icon: Icons.medication_outlined,
                        label: 'Médicaments',
                        onTap: () =>
                            Navigator.pushNamed(context, DosesScreen.route),
                      ),
                      _NavChip(
                        icon: Icons.event_outlined,
                        label: 'Rendez-vous',
                        onTap: () => Navigator.pushNamed(
                          context,
                          RendezVousScreen.route,
                        ),
                      ),
                      _NavChip(
                        icon: Icons.receipt_long_outlined,
                        label: 'Prescriptions',
                        onTap: () => Navigator.pushNamed(
                          context,
                          PrescriptionsScreen.route,
                        ),
                      ),
                      _NavChip(
                        icon: Icons.biotech_outlined,
                        label: 'Laboratoire',
                        onTap: () => Navigator.pushNamed(
                          context,
                          LaboratoireScreen.route,
                        ),
                      ),
                      _NavChip(
                        icon: Icons.request_quote_outlined,
                        label: 'Factures',
                        onTap: () =>
                            Navigator.pushNamed(context, FacturesScreen.route),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  _SectionTitle(title: 'Prochains médicaments'),
                  const SizedBox(height: 8),
                  if (_dashboard!.prochainesDoses.isEmpty)
                    const _EmptyCard(message: 'Aucune dose planifiée.')
                  else
                    ..._dashboard!.prochainesDoses.map(
                      (d) => _DoseTile(dose: d, formatDate: _formatDate),
                    ),
                  const SizedBox(height: 16),
                  _SectionTitle(title: 'Constantes récentes'),
                  const SizedBox(height: 8),
                  if (_dashboard!.constantesRecentes.isEmpty)
                    const _EmptyCard(message: 'Aucune constante enregistrée.')
                  else
                    ..._dashboard!.constantesRecentes.map(
                      (c) =>
                          _ConstanteTile(constante: c, formatDate: _formatDate),
                    ),
                ],
              ),
            ),
    );
  }
}

class _ProfilCard extends StatelessWidget {
  const _ProfilCard({required this.profil, this.userName});

  final PatientProfil profil;
  final String? userName;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            CircleAvatar(
              radius: 28,
              backgroundColor: Theme.of(context).colorScheme.primaryContainer,
              foregroundColor: Theme.of(context).colorScheme.primary,
              child: Text(
                profil.prenom.isNotEmpty ? profil.prenom[0].toUpperCase() : '?',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 20,
                ),
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '${profil.prenom} ${profil.nom}',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text('Dossier : ${profil.numeroDossier}'),
                  if (userName != null && userName!.isNotEmpty)
                    Text(
                      'Compte : $userName',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SummaryCard extends StatelessWidget {
  const _SummaryCard({
    required this.hospitalisation,
    required this.nextDoseCount,
    required this.recentVitalCount,
    required this.formatDate,
  });

  final HospitalisationResume? hospitalisation;
  final int nextDoseCount;
  final int recentVitalCount;
  final String Function(String) formatDate;

  @override
  Widget build(BuildContext context) {
    final hasHospitalisation = hospitalisation != null;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Résumé du jour',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 12,
              runSpacing: 12,
              children: [
                _SummaryPill(
                  icon: Icons.medication_outlined,
                  label: '$nextDoseCount dose(s) à venir',
                  isAlert: nextDoseCount > 0,
                ),
                _SummaryPill(
                  icon: Icons.monitor_heart_outlined,
                  label: '$recentVitalCount constante(s) récente(s)',
                ),
                _SummaryPill(
                  icon: hasHospitalisation
                      ? Icons.local_hotel_outlined
                      : Icons.info_outline,
                  label: hasHospitalisation
                      ? 'Hospitalisation en cours'
                      : 'Aucune hospitalisation active',
                  isAlert: hasHospitalisation,
                ),
              ],
            ),
            if (hasHospitalisation) ...[
              const SizedBox(height: 12),
              Text(
                'Dernier suivi : ${formatDate(hospitalisation!.dateAdmission)}',
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _SummaryPill extends StatelessWidget {
  const _SummaryPill({
    required this.icon,
    required this.label,
    this.isAlert = false,
  });

  final IconData icon;
  final String label;
  final bool isAlert;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: isAlert
            ? Theme.of(
                context,
              ).colorScheme.tertiaryContainer.withValues(alpha: 0.4)
            : Theme.of(
                context,
              ).colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            size: 16,
            color: isAlert ? Theme.of(context).colorScheme.primary : null,
          ),
          const SizedBox(width: 8),
          Flexible(
            child: Text(
              label,
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
          ),
        ],
      ),
    );
  }
}

class _HospitalisationCard extends StatelessWidget {
  const _HospitalisationCard({
    required this.hospitalisation,
    required this.formatDate,
  });

  final HospitalisationResume? hospitalisation;
  final String Function(String) formatDate;

  @override
  Widget build(BuildContext context) {
    if (hospitalisation == null) {
      return const Card(
        child: ListTile(
          leading: Icon(Icons.info_outline),
          title: Text('Pas d\'hospitalisation active'),
          subtitle: Text('Vous n\'êtes pas hospitalisé actuellement.'),
        ),
      );
    }

    final h = hospitalisation!;
    return Card(
      color: Theme.of(
        context,
      ).colorScheme.primaryContainer.withValues(alpha: 0.35),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Hospitalisation en cours',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            Text('Motif : ${h.motifAdmission}'),
            Text('Admission : ${formatDate(h.dateAdmission)}'),
            Text(
              'Lit : ${h.batimentCode}/${h.serviceCode} — Ch.${h.chambreNumero} Lit ${h.litNumero}',
            ),
          ],
        ),
      ),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  const _SectionTitle({required this.title});

  final String title;

  @override
  Widget build(BuildContext context) {
    return Text(title, style: Theme.of(context).textTheme.titleMedium);
  }
}

class _NavChip extends StatelessWidget {
  const _NavChip({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Theme.of(
        context,
      ).colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                icon,
                size: 20,
                color: Theme.of(context).colorScheme.primary,
              ),
              const SizedBox(width: 8),
              Text(label, style: const TextStyle(fontWeight: FontWeight.w600)),
            ],
          ),
        ),
      ),
    );
  }
}

class _DoseTile extends StatelessWidget {
  const _DoseTile({required this.dose, required this.formatDate});

  final DoseMedicament dose;
  final String Function(String) formatDate;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: Icon(
          dose.estEnRetard
              ? Icons.warning_amber_rounded
              : Icons.medication_outlined,
          color: dose.estEnRetard ? Colors.orange.shade800 : null,
        ),
        title: Text(dose.medicament),
        subtitle: Text('${dose.posologie} — ${formatDate(dose.heurePrevue)}'),
        trailing: dose.estEnRetard
            ? const Text('En retard', style: TextStyle(color: Colors.orange))
            : null,
      ),
    );
  }
}

class _ConstanteTile extends StatelessWidget {
  const _ConstanteTile({required this.constante, required this.formatDate});

  final ConstanteVitale constante;
  final String Function(String) formatDate;

  @override
  Widget build(BuildContext context) {
    final parts = <String>[];
    if (constante.temperature != null)
      parts.add('T° ${constante.temperature}°C');
    if (constante.tensionSystolique != null) {
      parts.add(
        'TA ${constante.tensionSystolique}/${constante.tensionDiastolique ?? '-'}',
      );
    }
    if (constante.frequenceCardiaque != null)
      parts.add('FC ${constante.frequenceCardiaque}');
    if (constante.saturationO2 != null)
      parts.add('SpO₂ ${constante.saturationO2}%');

    return Card(
      child: ListTile(
        leading: const Icon(Icons.monitor_heart_outlined),
        title: Text(parts.isEmpty ? 'Mesure enregistrée' : parts.join(' · ')),
        subtitle: Text(formatDate(constante.mesureLe)),
      ),
    );
  }
}

class _EmptyCard extends StatelessWidget {
  const _EmptyCard({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(padding: const EdgeInsets.all(16), child: Text(message)),
    );
  }
}
