import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;
import 'package:mime/mime.dart';
import 'package:http_parser/http_parser.dart';

import 'api_client.dart';
import 'api_config.dart';

class ReadingsApi {
  final ApiClient client;
  ReadingsApi(this.client);

  Future<Map<String, dynamic>> predict(File imageFile) async {
    final token = await client.getToken();
    final uri = Uri.parse('${ApiConfig.baseUrl}/api/readings/predict');

    final request = http.MultipartRequest('POST', uri);

    if (token != null) {
      request.headers['Authorization'] = 'Bearer $token';
    }

    final mime = lookupMimeType(imageFile.path) ?? 'image/jpeg';
    final parts = mime.split('/');

    request.files.add(
      await http.MultipartFile.fromPath(
        'image',
        imageFile.path,
        contentType: MediaType(parts[0], parts[1]),
      ),
    );

    final streamed = await request.send();
    final res = await http.Response.fromStream(streamed);

    if (res.statusCode != 200) {
      throw Exception(res.body);
    }

    return jsonDecode(res.body); // {category, confidence}
  }

  Future<void> createReading({
    required int? teamId,
    required String category, // arroz/feijao/outros
    required double? confidence,
  }) async {
    final res = await client.post('/api/readings', body: {
      'team_id': teamId,
      'category': category,
      'confidence': confidence,
    });

    if (res.statusCode != 200) {
      throw Exception(res.body);
    }
  }
}