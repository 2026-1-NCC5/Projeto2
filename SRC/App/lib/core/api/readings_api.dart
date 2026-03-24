import 'dart:io';
import 'api_client.dart';

class ReadingsApi {
  final ApiClient client;
  ReadingsApi(this.client);

  Future<Map<String, dynamic>> predict(File imageFile) async {
    return {
      'category': 'outros',
      'confidence': 0.80,
      'image_path': null,
    };
  }

  Future<void> createReading({
    required int? teamId,
    required String category,
    required double? confidence,
    String? imagePath,
  }) async {
    final res = await client.post('/api/readings', body: {
      'team_id': teamId,
      'category': category,
      'confidence': confidence,
      'image_path': imagePath,
    });

    if (res.statusCode != 200) {
      throw Exception(res.body);
    }
  }
}