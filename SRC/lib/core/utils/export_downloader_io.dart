import 'dart:io';
import 'package:path_provider/path_provider.dart';

Future<void> downloadCsv(String filename, String content) async {
  final dir = await getApplicationDocumentsDirectory();
  final file = File('${dir.path}/$filename');
  await file.writeAsString(content, flush: true);
}