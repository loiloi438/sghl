import 'package:flutter/material.dart';

import 'package:intl/intl.dart';

import 'package:provider/provider.dart';



import '../core/api_errors.dart';
import '../core/sghl_theme.dart';

import '../models/patient_models.dart';

import '../services/notification_inbox_service.dart';

import '../services/patient_services.dart';

import '../widgets/sghl_design_system.dart';
import '../widgets/human_care_widgets.dart';

import 'constantes_screen.dart';
import 'doses_screen.dart';
import 'factures_screen.dart';
import 'hospitalisations_screen.dart';
import 'laboratoire_screen.dart';
import 'notifications_screen.dart';
import 'plans_screen.dart';
import 'prescriptions_screen.dart';
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

      if (mounted) setState(() => _error = friendlyApiError(e));

    } finally {

      if (mounted) setState(() => _loading = false);

    }

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
    final bottomPad = widget.embedded ? HomeScreen.shellBottomPadding : 16.0;
    final unread = context.watch<NotificationInboxService>().unreadCount;



    return Scaffold(
      body: SghlHumanCareBackground(
        child: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null

              ? Padding(

                  padding: EdgeInsets.fromLTRB(16, 48, 16, bottomPad),

                  child: Column(

                    mainAxisAlignment: MainAxisAlignment.center,

                    children: [

                      SghlFeedbackBanner(

                        message: _error!,

                        type: SghlFeedbackType.error,

                      ),

                      const SizedBox(height: 16),

                      SghlGradientButton(

                        label: 'Réessayer',

                        onPressed: _load,

                      ),

                    ],

                  ),

                )

              : RefreshIndicator(

                  onRefresh: _load,

                  color: Theme.of(context).colorScheme.primary,

                  child: CustomScrollView(

                    physics: const AlwaysScrollableScrollPhysics(),

                    slivers: [

                      if (_dashboard != null)
                        SliverToBoxAdapter(
                          child: SghlHumanCareHero(
                            prenom: _dashboard!.profil.prenom,
                            wellnessMessage: _dashboard!.messageBienveillance.isNotEmpty
                                ? _dashboard!.messageBienveillance
                                : 'Vous êtes en bonne santé 💙',
                            trailing: IconButton(
                              onPressed: () => Navigator.pushNamed(
                                context,
                                NotificationsScreen.route,
                              ),
                              icon: Badge(
                                isLabelVisible: unread > 0,
                                label: Text('$unread'),
                                child: const Icon(
                                  Icons.notifications_outlined,
                                  color: SghlColors.humanCareTeal,
                                  size: 28,
                                ),
                              ),
                            ),
                          ),
                        ),

                      SliverPadding(

                        padding: EdgeInsets.fromLTRB(16, 8, 16, bottomPad),

                        sliver: SliverList(

                          delegate: SliverChildListDelegate([

                            if (_dashboard != null) ...[
                              Row(
                                children: [
                                  SghlHumanCareStatCard(
                                    value: _dashboard!.hospitalisationActive != null
                                        ? 'En cours'
                                        : '—',
                                    label: 'Hospitalisation',
                                    detail: _dashboard!.hospitalisationActive != null
                                        ? (_dashboard!.hospitalisationActive!.serviceNom.isNotEmpty
                                            ? _dashboard!.hospitalisationActive!.serviceNom
                                            : 'Suivi actif')
                                        : 'Bonne santé 💙',
                                    icon: Icons.local_hospital_outlined,
                                    backgroundColor: SghlColors.humanCareSky,
                                    borderColor: const Color(0xFFBAE6FD),
                                    labelColor: const Color(0xFF0369A1),
                                  ),
                                  const SizedBox(width: 8),
                                  SghlHumanCareStatCard(
                                    value: '${_dashboard!.prochainesDoses.length}',
                                    label: 'Doses à venir',
                                    detail: _dashboard!.prochainesDoses.isEmpty
                                        ? 'Rien de prévu'
                                        : _dashboard!.prochainesDoses.first.medicament,
                                    icon: Icons.medication_outlined,
                                    backgroundColor: SghlColors.humanCareLavender,
                                    borderColor: const Color(0xFFDDD6FE),
                                    labelColor: const Color(0xFF6D28D9),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Row(
                                children: [
                                  SghlHumanCareStatCard(
                                    value: '${_dashboard!.constantesRecentes.length}',
                                    label: 'Constantes',
                                    icon: Icons.monitor_heart_outlined,
                                    backgroundColor: SghlColors.humanCareSand,
                                    borderColor: const Color(0xFFFDE68A),
                                    labelColor: const Color(0xFFB45309),
                                  ),
                                  const SizedBox(width: 8),
                                  SghlHumanCareStatCard(
                                    value: '${_dashboard!.prochainsRdv.length}',
                                    label: 'Rendez-vous',
                                    detail: _dashboard!.prochainsRdv.isEmpty
                                        ? 'Planifiez une visite'
                                        : _formatDate(_dashboard!.prochainsRdv.first.dateHeure),
                                    icon: Icons.calendar_month_outlined,
                                    backgroundColor: const Color(0xFFECFDF5),
                                    borderColor: const Color(0xFFA7F3D0),
                                    labelColor: SghlColors.humanCareTeal,
                                  ),
                                ],
                              ),
                              const SizedBox(height: 16),
                              SghlHumanCareButton(
                                label: 'Prendre rendez-vous',
                                icon: Icons.calendar_month_rounded,
                                onPressed: () => Navigator.pushNamed(
                                  context,
                                  RendezVousScreen.route,
                                ),
                              ),

                              _HospitalisationCard(
                                hospitalisation: _dashboard!.hospitalisationActive,
                                formatDate: _formatDate,
                                onTap: () => Navigator.pushNamed(
                                  context,
                                  HospitalisationsScreen.route,
                                ),
                              ),

                              const SizedBox(height: kSectionSpacing),

                              const SghlSectionHeader(title: 'Raccourcis'),

                              const SizedBox(height: 16),

                              GridView.count(

                                crossAxisCount: 2,

                                shrinkWrap: true,

                                physics: const NeverScrollableScrollPhysics(),

                                mainAxisSpacing: 12,

                                crossAxisSpacing: 12,

                                childAspectRatio: 1.35,

                                children: [

                                  SghlShortcutTile(
                                    icon: Icons.local_hospital_outlined,
                                    label: 'Hospitalisation',
                                    color: SghlColors.humanCareTeal,
                                    onTap: () => Navigator.pushNamed(
                                      context,
                                      HospitalisationsScreen.route,
                                    ),
                                  ),
                                  SghlShortcutTile(
                                    icon: Icons.monitor_heart_outlined,
                                    label: 'Constantes',
                                    color: const Color(0xFF0369A1),

                                    onTap: () => Navigator.pushNamed(

                                      context,

                                      ConstantesScreen.route,

                                    ),

                                  ),

                                  SghlShortcutTile(
                                    icon: Icons.medical_services_outlined,
                                    label: 'Soins',
                                    color: const Color(0xFF6D28D9),

                                    onTap: () => Navigator.pushNamed(

                                      context,

                                      PlansScreen.route,

                                    ),

                                  ),

                                  SghlShortcutTile(
                                    icon: Icons.medication_outlined,
                                    label: 'Médicaments',
                                    color: const Color(0xFFB45309),

                                    onTap: () => Navigator.pushNamed(

                                      context,

                                      DosesScreen.route,

                                    ),

                                  ),

                                  SghlShortcutTile(
                                    icon: Icons.calendar_month_outlined,
                                    label: 'Rendez-vous',
                                    color: SghlColors.humanCareTeal,

                                    onTap: () => Navigator.pushNamed(

                                      context,

                                      RendezVousScreen.route,

                                    ),

                                  ),

                                  SghlShortcutTile(
                                    icon: Icons.description_outlined,
                                    label: 'Ordonnances',
                                    color: const Color(0xFF0D9488),

                                    onTap: () => Navigator.pushNamed(

                                      context,

                                      PrescriptionsScreen.route,

                                    ),

                                  ),

                                  SghlShortcutTile(
                                    icon: Icons.science_outlined,
                                    label: 'Laboratoire',
                                    color: const Color(0xFF0369A1),
                                    onTap: () => Navigator.pushNamed(
                                      context,
                                      LaboratoireScreen.route,
                                    ),
                                  ),
                                  SghlShortcutTile(
                                    icon: Icons.receipt_long_outlined,
                                    label: 'Factures',
                                    color: const Color(0xFF059669),

                                    onTap: () => Navigator.pushNamed(

                                      context,

                                      FacturesScreen.route,

                                    ),

                                  ),

                                ],

                              ),

                              const SizedBox(height: kSectionSpacing),

                              const SghlSectionHeader(

                                title: 'Prochains médicaments',

                              ),

                              const SizedBox(height: 16),

                              if (_dashboard!.prochainesDoses.isEmpty)

                                const SghlEmptyState(

                                  icon: Icons.medication_outlined,

                                  message: 'Aucune dose planifiée',

                                  subtitle:

                                      'Vos prochains médicaments apparaîtront ici.',

                                )

                              else

                                ..._dashboard!.prochainesDoses.map(

                                  (d) => Padding(

                                    padding: const EdgeInsets.only(bottom: 10),

                                    child: _DoseTile(

                                      dose: d,

                                      formatDate: _formatDate,

                                    ),

                                  ),

                                ),

                              const SizedBox(height: kSectionSpacing),

                              const SghlSectionHeader(

                                title: 'Constantes récentes',

                              ),

                              const SizedBox(height: 16),

                              if (_dashboard!.constantesRecentes.isEmpty)

                                const SghlEmptyState(

                                  icon: Icons.monitor_heart_outlined,

                                  message: 'Aucune constante enregistrée',

                                  subtitle:

                                      'Vos dernières mesures vitales s\'afficheront ici.',

                                )

                              else

                                ..._dashboard!.constantesRecentes.map(

                                  (c) => Padding(

                                    padding: const EdgeInsets.only(bottom: 10),

                                    child: _ConstanteTile(

                                      constante: c,

                                      formatDate: _formatDate,

                                    ),

                                  ),

                                ),

                            ],

                          ]),

                        ),

                      ),

                    ],

                  ),

                ),
      ),
    );
  }
}



class _HospitalisationCard extends StatelessWidget {
  const _HospitalisationCard({
    required this.hospitalisation,
    required this.formatDate,
    this.onTap,
  });

  final HospitalisationResume? hospitalisation;
  final String Function(String) formatDate;
  final VoidCallback? onTap;



  @override

  Widget build(BuildContext context) {

    if (hospitalisation == null) {
      return SghlCard(
        lightSurface: true,
        padding: const EdgeInsets.all(16),
        onTap: onTap,
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: SghlColors.humanCareSky,
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.favorite_rounded,
                color: SghlColors.humanCareTeal,
                size: 22,
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Vous êtes en bonne santé 💙',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w700,
                          color: SghlColors.humanCareText,
                        ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Aucune hospitalisation en cours — prenez soin de vous.',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ],
              ),
            ),
          ],
        ),
      );
    }

    final h = hospitalisation!;
    return SghlCard(
      lightSurface: true,
      padding: const EdgeInsets.all(16),
      onTap: onTap,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Votre séjour en cours',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                  color: SghlColors.humanCareText,
                ),
          ),
          const SizedBox(height: 8),
          Text('Motif : ${h.motifAdmission}'),
          if (h.medecinNom.isNotEmpty) Text('Médecin : ${h.medecinNom}'),
          if (h.serviceNom.isNotEmpty) Text('Service : ${h.serviceNom}'),
          Text('Admission : ${formatDate(h.dateAdmission)}'),
          Text(
            'Lit : ${h.batimentCode}/${h.serviceCode} — Ch.${h.chambreNumero} Lit ${h.litNumero}',
          ),
        ],
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

    return SghlCard(

      lightSurface: true,

      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),

      child: Row(

        children: [

          Icon(

            dose.estEnRetard

                ? Icons.warning_amber_rounded

                : Icons.medication_outlined,

            color: dose.estEnRetard ? SghlColors.gold : SghlColors.medicalBlue,

          ),

          const SizedBox(width: 12),

          Expanded(

            child: Column(

              crossAxisAlignment: CrossAxisAlignment.start,

              children: [

                Text(
                  dose.medicament,
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),

                Text('${dose.posologie} — ${formatDate(dose.heurePrevue)}'),

              ],

            ),

          ),

          if (dose.estEnRetard)
            Text(
              'En retard',
              style: Theme.of(context).textTheme.labelMedium?.copyWith(
                    color: SghlColors.gold,
                    fontWeight: FontWeight.w600,
                  ),
            ),

        ],

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

    if (constante.temperature != null) {

      parts.add('T° ${constante.temperature}°C');

    }

    if (constante.tensionSystolique != null) {

      parts.add(

        'TA ${constante.tensionSystolique}/${constante.tensionDiastolique ?? '-'}',

      );

    }

    if (constante.frequenceCardiaque != null) {

      parts.add('FC ${constante.frequenceCardiaque}');

    }

    if (constante.saturationO2 != null) {

      parts.add('SpO₂ ${constante.saturationO2}%');

    }



    return SghlCard(

      lightSurface: true,

      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),

      child: Row(

        children: [

          const Icon(Icons.monitor_heart_outlined,

              color: SghlColors.medicalBlue),

          const SizedBox(width: 12),

          Expanded(

            child: Column(

              crossAxisAlignment: CrossAxisAlignment.start,

              children: [

                Text(
                  parts.isEmpty ? 'Mesure enregistrée' : parts.join(' · '),
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),

                Text(formatDate(constante.mesureLe)),

              ],

            ),

          ),

        ],

      ),

    );

  }

}


