import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../core/api_errors.dart';
import '../core/sghl_theme.dart';
import '../models/patient_models.dart';
import '../services/notification_inbox_service.dart';
import '../services/patient_services.dart';
import '../widgets/human_care_auth_layout.dart';
import '../widgets/human_care_widgets.dart';
import '../widgets/sghl_design_system.dart';
import 'factures_screen.dart';
import 'laboratoire_screen.dart';
import 'messagerie_screen.dart';
import 'notifications_screen.dart';
import 'prescriptions_screen.dart';
import 'profil_screen.dart';
import 'rendez_vous_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key, this.embedded = false});

  static const route = '/home';
  static const double shellBottomPadding = kPatientShellBottomPadding;

  final bool embedded;

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  TableauBord? _dashboard;
  List<PrescriptionPatient> _prescriptions = const [];
  List<ResultatLaboPatient> _analyses = const [];
  List<FacturePatient> _factures = const [];
  List<PatientMessage> _messages = const [];
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
      final service = context.read<PatientService>();
      final results = await Future.wait<dynamic>([
        service.fetchDashboard(),
        service.fetchPrescriptions(),
        service.fetchResultatsLaboratoire(),
        service.fetchFactures(),
        service.fetchMessages(),
      ]);
      if (!mounted) return;
      setState(() {
        _dashboard = results[0] as TableauBord;
        _prescriptions = results[1] as List<PrescriptionPatient>;
        _analyses = results[2] as List<ResultatLaboPatient>;
        _factures = results[3] as List<FacturePatient>;
        _messages = results[4] as List<PatientMessage>;
      });
      await context.read<NotificationInboxService>().refresh();
    } catch (error) {
      if (mounted) setState(() => _error = friendlyApiError(error));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  String _date(String iso, {bool timeOnly = false}) {
    try {
      final date = DateTime.parse(iso).toLocal();
      return DateFormat(timeOnly ? 'HH:mm' : 'dd/MM/yyyy').format(date);
    } catch (_) {
      return iso;
    }
  }

  FacturePatient? get _pendingInvoice {
    for (final invoice in _factures) {
      if (invoice.statut != 'payee' && invoice.statut != 'annulee') {
        return invoice;
      }
    }
    return null;
  }

  ResultatLaboPatient? get _latestAnalysis =>
      _analyses.isEmpty ? null : _analyses.first;

  RendezVousPatient? get _nextAppointment {
    final items = _dashboard?.prochainsRdv ?? const <RendezVousPatient>[];
    return items.isEmpty ? null : items.first;
  }

  @override
  Widget build(BuildContext context) {
    final bottomPadding = widget.embedded
        ? HomeScreen.shellBottomPadding + 12
        : 24.0;
    return Scaffold(
      body: SghlHumanCareBackground(
        child: _loading
            ? const SghlHumanCareHeartLoader()
            : _error != null
            ? _ErrorState(message: _error!, onRetry: _load)
            : RefreshIndicator(
                onRefresh: _load,
                color: SghlColors.humanCareTeal,
                child: CustomScrollView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  slivers: [
                    SliverToBoxAdapter(child: _header()),
                    SliverPadding(
                      padding: EdgeInsets.fromLTRB(16, 4, 16, bottomPadding),
                      sliver: SliverList.list(
                        children: [
                          _summaryCards(),
                          const SizedBox(height: 14),
                          _wellnessCard(),
                          const SizedBox(height: 14),
                          _appointmentCard(),
                          const SizedBox(height: 12),
                          Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Expanded(child: _analysisCard()),
                              const SizedBox(width: 12),
                              Expanded(child: _invoiceCard()),
                            ],
                          ),
                          const SizedBox(height: 12),
                          Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Expanded(child: _messagesCard()),
                              const SizedBox(width: 12),
                              Expanded(child: _wellnessAdviceCard()),
                            ],
                          ),
                          const SizedBox(height: 12),
                          _historyCard(),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
      ),
    );
  }

  Widget _header() {
    final unread = context.watch<NotificationInboxService>().unreadCount;
    return SafeArea(
      bottom: false,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(18, 14, 14, 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Expanded(child: SghlHumanCareLogo(compact: true)),
                _HeaderAction(
                  icon: Icons.mail_outline_rounded,
                  onTap: () =>
                      Navigator.pushNamed(context, MessagerieScreen.route),
                ),
                const SizedBox(width: 7),
                _HeaderAction(
                  icon: Icons.notifications_none_rounded,
                  badge: unread,
                  onTap: () =>
                      Navigator.pushNamed(context, NotificationsScreen.route),
                ),
                const SizedBox(width: 7),
                InkWell(
                  onTap: () => Navigator.pushNamed(context, ProfilScreen.route),
                  borderRadius: BorderRadius.circular(999),
                  child: Container(
                    width: 42,
                    height: 42,
                    decoration: const BoxDecoration(
                      shape: BoxShape.circle,
                      gradient: LinearGradient(
                        colors: [Color(0xFF7DD3FC), Color(0xFF2DD4BF)],
                      ),
                    ),
                    child: const Icon(
                      Icons.person_rounded,
                      color: Colors.white,
                      size: 26,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 22),
            Text(
              'Bonjour, ${_dashboard!.profil.prenom} 💙',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontSize: 27,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 3),
            Text(
              'Prenez soin de vous, nous restons à vos côtés.',
              style: Theme.of(
                context,
              ).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w600),
            ),
          ],
        ),
      ),
    );
  }

  Widget _summaryCards() {
    final appointments = _dashboard!.prochainsRdv.length;
    final activePrescriptions = _prescriptions
        .where((p) => p.statut != 'annulee' && p.statutPharmacie != 'retiree')
        .length;
    final pendingInvoices = _factures
        .where((f) => f.statut != 'payee' && f.statut != 'annulee')
        .length;
    return Row(
      children: [
        Expanded(
          child: _KpiCard(
            icon: Icons.calendar_month_outlined,
            label: 'Rendez-vous',
            value: '$appointments',
            tint: const Color(0xFFE0F7FA),
            color: const Color(0xFF0EA5A8),
            onTap: () => Navigator.pushNamed(context, RendezVousScreen.route),
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _KpiCard(
            icon: Icons.medication_outlined,
            label: 'Ordonnances',
            value: '$activePrescriptions',
            tint: const Color(0xFFECFDF5),
            color: SghlColors.humanCareTeal,
            onTap: () =>
                Navigator.pushNamed(context, PrescriptionsScreen.route),
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _KpiCard(
            icon: Icons.account_balance_wallet_outlined,
            label: 'Factures',
            value: '$pendingInvoices',
            tint: const Color(0xFFFFF7E6),
            color: const Color(0xFFFF9F1C),
            onTap: () => Navigator.pushNamed(context, FacturesScreen.route),
          ),
        ),
      ],
    );
  }

  Widget _wellnessCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: _cardDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFFE0F7FA), Color(0xFFECFDF5)],
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Vous êtes entre de bonnes mains 💙',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w800,
                    fontSize: 16,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  _dashboard!.messageBienveillance.isEmpty
                      ? 'Notre équipe veille sur votre parcours de soins.'
                      : _dashboard!.messageBienveillance,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
          Container(
            width: 70,
            height: 70,
            decoration: const BoxDecoration(
              color: Colors.white,
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.health_and_safety_rounded,
              color: SghlColors.humanCareTeal,
              size: 40,
            ),
          ),
        ],
      ),
    );
  }

  Widget _appointmentCard() {
    final appointment = _nextAppointment;
    return _DashboardCard(
      child: appointment == null
          ? _EmptyAction(
              icon: Icons.event_available_outlined,
              title: 'Aucun rendez-vous à venir',
              action: 'Prendre rendez-vous',
              onTap: () => Navigator.pushNamed(context, RendezVousScreen.route),
            )
          : Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const _CardTitle(
                  icon: Icons.calendar_month_outlined,
                  title: 'Prochain rendez-vous',
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Container(
                      width: 64,
                      height: 64,
                      decoration: const BoxDecoration(
                        color: Color(0xFFE0F2FE),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.medical_services_rounded,
                        color: Color(0xFF0284C7),
                        size: 34,
                      ),
                    ),
                    const SizedBox(width: 13),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '${_date(appointment.dateHeure)} · ${_date(appointment.dateHeure, timeOnly: true)}',
                            style: const TextStyle(
                              color: SghlColors.humanCareTeal,
                              fontWeight: FontWeight.w800,
                              fontSize: 15,
                            ),
                          ),
                          const SizedBox(height: 3),
                          Text(
                            appointment.motif,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: Theme.of(
                              context,
                            ).textTheme.titleMedium?.copyWith(fontSize: 16),
                          ),
                          Text(
                            appointment.medecinNom,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: FilledButton(
                        onPressed: () => Navigator.pushNamed(
                          context,
                          RendezVousScreen.route,
                        ),
                        child: const Text('Voir le détail'),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: OutlinedButton(
                        onPressed: () => Navigator.pushNamed(
                          context,
                          RendezVousScreen.route,
                        ),
                        child: const Text('Reprogrammer'),
                      ),
                    ),
                  ],
                ),
              ],
            ),
    );
  }

  Widget _analysisCard() {
    final analysis = _latestAnalysis;
    return _DashboardCard(
      minHeight: 180,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const _CardTitle(icon: Icons.science_outlined, title: 'Mes analyses'),
          const SizedBox(height: 12),
          Icon(
            Icons.biotech_rounded,
            size: 38,
            color: analysis == null
                ? SghlColors.humanCareMuted
                : const Color(0xFF38BDF8),
          ),
          const SizedBox(height: 8),
          Text(
            analysis?.analyses.join(', ') ?? 'Aucun résultat disponible',
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
              color: SghlColors.humanCareText,
              fontWeight: FontWeight.w800,
            ),
          ),
          const Spacer(),
          _TextAction(
            label: 'Voir le détail',
            onTap: () => Navigator.pushNamed(context, LaboratoireScreen.route),
          ),
        ],
      ),
    );
  }

  Widget _invoiceCard() {
    final invoice = _pendingInvoice;
    final amount = invoice?.montantRestant ?? '0';
    return _DashboardCard(
      minHeight: 180,
      tint: const Color(0xFFFFFCF2),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const _CardTitle(
            icon: Icons.account_balance_wallet_outlined,
            title: 'Facture',
            color: Color(0xFFFF9F1C),
          ),
          const SizedBox(height: 16),
          Text(
            invoice == null ? 'Tout est réglé' : '$amount FCFA',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
              color: SghlColors.humanCareText,
              fontWeight: FontWeight.w800,
            ),
          ),
          Text(
            invoice == null ? 'Aucun paiement en attente' : 'Montant à régler',
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const Spacer(),
          FilledButton(
            onPressed: () => Navigator.pushNamed(context, FacturesScreen.route),
            style: FilledButton.styleFrom(
              minimumSize: const Size.fromHeight(38),
              backgroundColor: const Color(0xFFFF9F1C),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 8),
            ),
            child: Text(invoice == null ? 'Voir mes factures' : 'Payer'),
          ),
        ],
      ),
    );
  }

  Widget _messagesCard() {
    return _DashboardCard(
      minHeight: 190,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const _CardTitle(
            icon: Icons.chat_bubble_outline_rounded,
            title: 'Messages récents',
          ),
          const SizedBox(height: 9),
          if (_messages.isEmpty)
            const Text('Aucun message récent.')
          else
            ..._messages
                .take(2)
                .map(
                  (message) => Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Row(
                      children: [
                        const Icon(
                          Icons.mail_outline_rounded,
                          size: 18,
                          color: SghlColors.humanCareTeal,
                        ),
                        const SizedBox(width: 7),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                message.expediteurNom.isEmpty
                                    ? 'SGHL'
                                    : message.expediteurNom,
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.w800,
                                ),
                              ),
                              Text(
                                message.sujet,
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(fontSize: 11),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
          const Spacer(),
          _TextAction(
            label: 'Voir tous',
            onTap: () => Navigator.pushNamed(context, MessagerieScreen.route),
          ),
        ],
      ),
    );
  }

  Widget _wellnessAdviceCard() {
    return const _DashboardCard(
      minHeight: 190,
      tint: Color(0xFFF3FFFB),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _CardTitle(icon: Icons.eco_outlined, title: 'Conseils santé'),
          SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.apple_rounded, size: 38, color: Color(0xFFFF8A65)),
              Icon(
                Icons.local_drink_outlined,
                size: 36,
                color: Color(0xFF38BDF8),
              ),
            ],
          ),
          SizedBox(height: 10),
          Text(
            'Adoptez une alimentation équilibrée et restez actif au quotidien.',
            maxLines: 4,
            overflow: TextOverflow.ellipsis,
            style: TextStyle(fontSize: 12, height: 1.35),
          ),
        ],
      ),
    );
  }

  Widget _historyCard() {
    final vitals = _dashboard!.constantesRecentes.take(2).toList();
    return _DashboardCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const _CardTitle(icon: Icons.history_rounded, title: 'Historique'),
          const SizedBox(height: 8),
          if (vitals.isEmpty)
            const Text('Votre historique médical apparaîtra ici.')
          else
            ...vitals.map(
              (vital) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 6),
                child: Row(
                  children: [
                    const Icon(
                      Icons.monitor_heart_outlined,
                      size: 19,
                      color: SghlColors.humanCareTeal,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      _date(vital.mesureLe),
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                    const Spacer(),
                    Text(
                      vital.temperature == null
                          ? 'Constantes enregistrées'
                          : 'Température ${vital.temperature}°C',
                      style: const TextStyle(fontSize: 12),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}

BoxDecoration _cardDecoration({Gradient? gradient, Color? color}) {
  return BoxDecoration(
    color: gradient == null ? (color ?? Colors.white) : null,
    gradient: gradient,
    borderRadius: BorderRadius.circular(20),
    border: Border.all(color: const Color(0xFFCCFBF1)),
    boxShadow: [
      BoxShadow(
        color: const Color(0xFF0D9488).withValues(alpha: 0.09),
        blurRadius: 18,
        offset: const Offset(0, 7),
      ),
    ],
  );
}

class _DashboardCard extends StatelessWidget {
  const _DashboardCard({required this.child, this.minHeight, this.tint});

  final Widget child;
  final double? minHeight;
  final Color? tint;

  @override
  Widget build(BuildContext context) {
    return Container(
      constraints: BoxConstraints(minHeight: minHeight ?? 0),
      padding: const EdgeInsets.all(14),
      decoration: _cardDecoration(color: tint),
      child: child,
    );
  }
}

class _KpiCard extends StatelessWidget {
  const _KpiCard({
    required this.icon,
    required this.label,
    required this.value,
    required this.tint,
    required this.color,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final String value;
  final Color tint;
  final Color color;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(18),
      child: Container(
        height: 108,
        padding: const EdgeInsets.all(11),
        decoration: _cardDecoration(),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(7),
              decoration: BoxDecoration(
                color: tint,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, size: 21, color: color),
            ),
            const Spacer(),
            Text(
              label,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w800,
                color: SghlColors.humanCareText,
              ),
            ),
            Text(
              value,
              style: TextStyle(
                fontSize: 20,
                height: 1,
                fontWeight: FontWeight.w900,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _CardTitle extends StatelessWidget {
  const _CardTitle({
    required this.icon,
    required this.title,
    this.color = SghlColors.humanCareTeal,
  });

  final IconData icon;
  final String title;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 21, color: color),
        const SizedBox(width: 7),
        Expanded(
          child: Text(
            title,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
              color: SghlColors.humanCareText,
              fontWeight: FontWeight.w800,
              fontSize: 14,
            ),
          ),
        ),
      ],
    );
  }
}

class _HeaderAction extends StatelessWidget {
  const _HeaderAction({
    required this.icon,
    required this.onTap,
    this.badge = 0,
  });

  final IconData icon;
  final VoidCallback onTap;
  final int badge;

  @override
  Widget build(BuildContext context) {
    return IconButton.filledTonal(
      onPressed: onTap,
      style: IconButton.styleFrom(
        backgroundColor: Colors.white,
        foregroundColor: SghlColors.humanCareText,
        side: const BorderSide(color: Color(0xFFCCFBF1)),
      ),
      icon: Badge(
        isLabelVisible: badge > 0,
        label: Text(badge > 9 ? '9+' : '$badge'),
        child: Icon(icon),
      ),
    );
  }
}

class _TextAction extends StatelessWidget {
  const _TextAction({required this.label, required this.onTap});

  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            label,
            style: const TextStyle(
              color: SghlColors.humanCareTeal,
              fontWeight: FontWeight.w800,
              fontSize: 12,
            ),
          ),
          const Icon(
            Icons.chevron_right_rounded,
            color: SghlColors.humanCareTeal,
            size: 18,
          ),
        ],
      ),
    );
  }
}

class _EmptyAction extends StatelessWidget {
  const _EmptyAction({
    required this.icon,
    required this.title,
    required this.action,
    required this.onTap,
  });

  final IconData icon;
  final String title;
  final String action;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 38, color: SghlColors.humanCareTeal),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: const TextStyle(fontWeight: FontWeight.w800)),
              _TextAction(label: action, onTap: onTap),
            ],
          ),
        ),
      ],
    );
  }
}

class _ErrorState extends StatelessWidget {
  const _ErrorState({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            SghlFeedbackBanner(message: message, type: SghlFeedbackType.error),
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('Réessayer'),
            ),
          ],
        ),
      ),
    );
  }
}
