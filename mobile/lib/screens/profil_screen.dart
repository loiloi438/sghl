import 'package:flutter/material.dart';

import 'package:provider/provider.dart';



import '../core/api_errors.dart';
import '../core/sghl_theme.dart';
import '../models/patient_models.dart';
import '../services/patient_services.dart';
import '../widgets/human_care_widgets.dart';
import '../widgets/sghl_design_system.dart';
import '../widgets/patient_human_care_page.dart';
import 'login_screen.dart';



class ProfilScreen extends StatefulWidget {

  const ProfilScreen({super.key, this.embedded = false});



  static const route = '/profil';



  final bool embedded;



  @override

  State<ProfilScreen> createState() => _ProfilScreenState();

}



class _ProfilScreenState extends State<ProfilScreen> {

  PatientProfil? _profil;

  bool _loading = true;

  String? _error;

  Future<void> _editProfil() async {
    final profil = _profil;
    if (profil == null) return;

    final telephoneController = TextEditingController(text: profil.telephone);
    final emailController = TextEditingController(text: profil.email);
    final adresseController = TextEditingController(text: profil.adresse);

    final updated = await showDialog<PatientProfil>(
      context: context,
      builder: (dialogContext) {
        var saving = false;
        String? dialogError;
        return StatefulBuilder(
          builder: (context, setDialogState) => AlertDialog(
            title: const Text('Modifier mes coordonnées'),
            content: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (dialogError != null) ...[
                    SghlFeedbackBanner(
                      message: dialogError!,
                      type: SghlFeedbackType.error,
                    ),
                    const SizedBox(height: 12),
                  ],
                  TextField(
                    controller: telephoneController,
                    keyboardType: TextInputType.phone,
                    decoration: const InputDecoration(
                      labelText: 'Téléphone',
                      prefixIcon: Icon(Icons.phone_outlined),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: emailController,
                    keyboardType: TextInputType.emailAddress,
                    decoration: const InputDecoration(
                      labelText: 'E-mail',
                      prefixIcon: Icon(Icons.email_outlined),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: adresseController,
                    maxLines: 2,
                    decoration: const InputDecoration(
                      labelText: 'Adresse',
                      prefixIcon: Icon(Icons.home_outlined),
                    ),
                  ),
                ],
              ),
            ),
            actions: [
              TextButton(
                onPressed:
                    saving ? null : () => Navigator.of(dialogContext).pop(),
                child: const Text('Annuler'),
              ),
              FilledButton.icon(
                onPressed: saving
                    ? null
                    : () async {
                        final email = emailController.text.trim();
                        if (email.isNotEmpty && !email.contains('@')) {
                          setDialogState(
                            () => dialogError = 'Adresse e-mail invalide.',
                          );
                          return;
                        }
                        setDialogState(() {
                          saving = true;
                          dialogError = null;
                        });
                        try {
                          final result = await context
                              .read<PatientService>()
                              .updateProfil(
                                telephone: telephoneController.text,
                                email: email,
                                adresse: adresseController.text,
                              );
                          if (dialogContext.mounted) {
                            Navigator.of(dialogContext).pop(result);
                          }
                        } catch (e) {
                          if (dialogContext.mounted) {
                            setDialogState(() {
                              saving = false;
                              dialogError =
                                  friendlyApiError(e, isPatient: true);
                            });
                          }
                        }
                      },
                icon: saving
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.save_outlined),
                label: const Text('Enregistrer'),
              ),
            ],
          ),
        );
      },
    );

    telephoneController.dispose();
    emailController.dispose();
    adresseController.dispose();
    if (!mounted || updated == null) return;
    setState(() => _profil = updated);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Vos coordonnées ont été mises à jour 💙')),
    );
  }



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

    final bottomPad =

        widget.embedded ? kPatientShellBottomPadding : 16.0;



    return Scaffold(

      appBar: widget.embedded

          ? null

          : AppBar(title: const Text('Mon profil')),

      body: SghlHumanCareBackground(
        child: _loading

          ? const SghlHumanCareHeartLoader(
              message: 'Chargement de votre profil…',
            )

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

                    padding: EdgeInsets.fromLTRB(

                      16,

                      widget.embedded ? 48 : 16,

                      16,

                      bottomPad,

                    ),

                    children: [

                      if (widget.embedded)
                        PatientHcHeader(
                          title: 'Mon profil',
                          subtitle: 'Vos informations et paramètres 💙',
                          embedded: true,
                        ),

                      SghlCard(
                        lightSurface: true,

                        child: Column(

                          children: [

                            Container(

                              padding: const EdgeInsets.all(4),

                              decoration: BoxDecoration(

                                shape: BoxShape.circle,

                                gradient: SghlColors.humanCareCtaGradient,

                              ),

                              child: CircleAvatar(

                                radius: 36,

                                backgroundColor:

                                    Theme.of(context).cardTheme.color,

                                child: Text(

                                  _profil!.prenom.isNotEmpty

                                      ? _profil!.prenom[0].toUpperCase()

                                      : '?',

                                  style: SghlTypography.montserrat(
                                    fontSize: SghlTypography.display,
                                    fontWeight: FontWeight.w800,
                                    color: SghlColors.humanCareTeal,
                                  ),

                                ),

                              ),

                            ),

                            const SizedBox(height: 14),

                            Text(

                              '${_profil!.prenom} ${_profil!.nom}',

                              style:

                                  Theme.of(context).textTheme.headlineSmall,

                            ),

                            const SizedBox(height: 4),

                            Text(

                              'Dossier ${_profil!.numeroDossier}',

                              style: Theme.of(context).textTheme.bodyMedium

                                  ?.copyWith(

                                color: Theme.of(context).colorScheme.outline,

                              ),

                            ),

                          ],

                        ),

                      ),

                      const SizedBox(height: 16),

                      SghlCard(
                        lightSurface: true,

                        child: Column(

                          children: [

                            _InfoTile(

                              icon: Icons.cake_outlined,

                              label: 'Date de naissance',

                              value: _profil!.dateNaissance,

                            ),

                            _InfoTile(

                              icon: Icons.wc_outlined,

                              label: 'Sexe',

                              value: _profil!.sexe,

                            ),

                            _InfoTile(

                              icon: Icons.phone_outlined,

                              label: 'Téléphone',

                              value: _profil!.telephone,

                            ),

                            _InfoTile(

                              icon: Icons.email_outlined,

                              label: 'E-mail',

                              value: _profil!.email,

                            ),

                            _InfoTile(

                              icon: Icons.home_outlined,

                              label: 'Adresse',

                              value: _profil!.adresse,

                            ),

                          ],

                        ),

                      ),

                      const SizedBox(height: 12),

                      SghlHumanCareButton(
                        label: 'Modifier mes coordonnées',
                        icon: Icons.edit_outlined,
                        compact: true,
                        onPressed: _editProfil,
                      ),

                      if (auth.user != null) ...[

                        const SizedBox(height: 16),

                        SghlCard(
                        lightSurface: true,

                          child: Column(

                            crossAxisAlignment: CrossAxisAlignment.start,

                            children: [

                              Text(

                                'Compte',

                                style: Theme.of(context).textTheme.titleSmall,

                              ),

                              const SizedBox(height: 12),

                              _InfoTile(

                                icon: Icons.badge_outlined,

                                label: 'Identifiant',

                                value: auth.user!.username,

                              ),

                              _InfoTile(

                                icon: Icons.alternate_email,

                                label: 'E-mail compte',

                                value: auth.user!.email,

                              ),

                            ],

                          ),

                        ),

                      ],

                      const SizedBox(height: 20),

                      OutlinedButton.icon(

                        onPressed: () async {

                          await context.read<AuthService>().logout();

                          if (!context.mounted) return;

                          Navigator.of(context).pushNamedAndRemoveUntil(

                            LoginScreen.route,

                            (route) => false,

                          );

                        },

                        icon: const Icon(Icons.logout_rounded),

                        label: const Text('Se déconnecter'),

                      ),

                    ],

                  ),

                ),

      ),
    );

  }

}



class _InfoTile extends StatelessWidget {

  const _InfoTile({

    required this.icon,

    required this.label,

    required this.value,

  });



  final IconData icon;

  final String label;

  final String value;



  @override

  Widget build(BuildContext context) {

    if (value.isEmpty) return const SizedBox.shrink();

    return Padding(

      padding: const EdgeInsets.only(bottom: 14),

      child: Row(

        crossAxisAlignment: CrossAxisAlignment.start,

        children: [

          Icon(icon, size: 20, color: SghlColors.humanCareTeal),

          const SizedBox(width: 12),

          Expanded(

            child: Column(

              crossAxisAlignment: CrossAxisAlignment.start,

              children: [

                Text(label, style: Theme.of(context).textTheme.labelMedium),

                const SizedBox(height: 4),

                Text(value, style: Theme.of(context).textTheme.bodyLarge),

              ],

            ),

          ),

        ],

      ),

    );

  }

}


