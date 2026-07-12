import 'package:flutter/material.dart';

import '../core/api_client.dart';
import '../core/sghl_theme.dart';

class PdfDownloadButton extends StatefulWidget {
  const PdfDownloadButton({
    super.key,
    required this.label,
    required this.onDownload,
  });

  final String label;
  final Future<void> Function() onDownload;

  @override
  State<PdfDownloadButton> createState() => _PdfDownloadButtonState();
}

class _PdfDownloadButtonState extends State<PdfDownloadButton> {
  bool _loading = false;

  Future<void> _handlePress() async {
    setState(() => _loading = true);
    try {
      await widget.onDownload();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('${widget.label} ouvert.'),
          backgroundColor: SghlColors.humanCareTeal,
        ),
      );
    } on ApiException catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.message)),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erreur : $e')),
      );
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return OutlinedButton.icon(
      style: OutlinedButton.styleFrom(
        foregroundColor: const Color(0xFF065F46),
        side: const BorderSide(color: Color(0xFF99F6E4)),
        backgroundColor: const Color(0xFFECFDF5),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
      ),
      onPressed: _loading ? null : _handlePress,
      icon: _loading
          ? const SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(strokeWidth: 2),
            )
          : const Icon(Icons.picture_as_pdf_outlined, size: 18),
      label: Text(_loading ? 'Téléchargement…' : widget.label),
    );
  }
}
