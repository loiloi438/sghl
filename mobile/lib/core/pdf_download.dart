import 'dart:io';

import 'package:open_filex/open_filex.dart';
import 'package:path_provider/path_provider.dart';

class PdfDownloadHelper {
  static Future<File> savePdf(List<int> bytes, String filename) async {
    final dir = await getApplicationDocumentsDirectory();
    final safeName = filename.replaceAll(RegExp(r'[\\/:*?"<>|]'), '_');
    if (!safeName.toLowerCase().endsWith('.pdf')) {
      return _write('${dir.path}/$safeName.pdf', bytes);
    }
    return _write('${dir.path}/$safeName', bytes);
  }

  static Future<File> _write(String path, List<int> bytes) async {
    final file = File(path);
    await file.writeAsBytes(bytes, flush: true);
    return file;
  }

  static Future<void> saveAndOpen(List<int> bytes, String filename) async {
    final file = await savePdf(bytes, filename);
    final result = await OpenFilex.open(file.path, type: 'application/pdf');
    if (result.type != ResultType.done) {
      throw Exception(result.message);
    }
  }
}
