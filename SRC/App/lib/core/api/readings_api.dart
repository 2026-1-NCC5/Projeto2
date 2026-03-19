import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:mime/mime.dart';

class PredictResult {
  final String category;
  final double confidence;
  final String? imagePath;

  PredictResult({
    required this.category,
    required this.confidence,
    this.imagePath,
  });

  factory PredictResult.fromMap(Map<String, dynamic> map) {
    return PredictResult(
      category: (map['category'] ?? 'outros').toString(),
      confidence: map['confidence'] == null
          ? 0.0
          : (map['confidence'] as num).toDouble(),
      imagePath: map['image_path']?.toString(),
    );
  }
}

class ReadingsApi {
  ReadingsApi([Object? _ignored]);

  static const String baseUrl = 'http://127.0.0.1:8001';

  Future<PredictResult> predict(File imageFile) async {
    final uri = Uri.parse('$baseUrl/predict');

    final request = http.MultipartRequest('POST', uri);

    final mimeType = lookupMimeType(imageFile.path) ?? 'image/jpeg';
    final split = mimeType.split('/');

    request.files.add(
      await http.MultipartFile.fromPath(
        'image',
        imageFile.path,
        contentType: MediaType(split[0], split[1]),
      ),
    );

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode != 200) {
      throw Exception('Erro ao prever leitura: ${response.body}');
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return PredictResult.fromMap(data);
  }
}