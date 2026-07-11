import 'package:flutter/material.dart';

import '../core/api_config.dart';
import 'sghl_design_system.dart';

/// Configuration de l'URL API — indispensable sur telephone physique (meme Wi-Fi que le PC).
class ServerSettingsCard extends StatefulWidget {
  const ServerSettingsCard({
    super.key,
    this.initiallyExpanded = false,
  });

  final bool initiallyExpanded;

  @override
  State<ServerSettingsCard> createState() => ServerSettingsCardState();
}

class ServerSettingsCardState extends State<ServerSettingsCard> {
  late final TextEditingController _controller;
  bool _expanded = false;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: ApiConfig.baseUrl);
    _expanded = widget.initiallyExpanded;
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  /// Enregistre l'URL saisie. Retourne false si invalide ou vide.
  Future<bool> persistServerUrl(BuildContext context) async {
    final raw = _controller.text.trim();
    if (raw.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Indiquez l\'adresse du serveur SGHL (ex. http://192.168.1.10:8000/api/v1).',
          ),
        ),
      );
      return false;
    }

    final uri = Uri.tryParse(raw);
    if (uri == null ||
        !uri.hasScheme ||
        (uri.scheme != 'http' && uri.scheme != 'https') ||
        uri.host.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'URL serveur invalide. Exemple : http://192.168.1.10:8000/api/v1',
          ),
        ),
      );
      return false;
    }

    await ApiConfig.setBaseUrl(raw);
    return true;
  }

  @override
  Widget build(BuildContext context) {
    return SghlCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          InkWell(
            onTap: () => setState(() => _expanded = !_expanded),
            borderRadius: BorderRadius.circular(8),
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Row(
                children: [
                  Icon(
                    _expanded ? Icons.expand_less : Icons.expand_more,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Serveur SGHL',
                          style: Theme.of(context).textTheme.labelLarge?.copyWith(
                                fontWeight: FontWeight.w700,
                              ),
                        ),
                        if (!_expanded)
                          Text(
                            ApiConfig.baseUrl,
                            style: Theme.of(context).textTheme.bodySmall,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          if (_expanded) ...[
            const SizedBox(height: 8),
            Text(
              'Sur telephone, utilisez l\'adresse IP de votre PC (meme reseau Wi-Fi). '
              'Lancez le backend avec : python manage.py runserver 0.0.0.0:8000',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 10),
            TextFormField(
              controller: _controller,
              keyboardType: TextInputType.url,
              decoration: const InputDecoration(
                labelText: 'URL de l\'API',
                hintText: 'http://192.168.1.10:8000/api/v1',
              ),
            ),
          ],
        ],
      ),
    );
  }
}
