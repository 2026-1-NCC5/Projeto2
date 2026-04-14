import 'dart:convert';
import 'api_client.dart';

class ReadingsApi {
  final ApiClient client;
  ReadingsApi(this.client);

  Future<void> createReading({
    required int teamId,
    required String category,
    required double kgAmount,
  }) async {
    final res = await client.post('/api/readings', body: {
      'team_id': teamId,
      'category': category,
      'kg_amount': kgAmount,
    });
    if (res.statusCode != 200) {
      throw Exception('Erro ao registrar: ${res.body}');
    }
  }

  Future<List<Map<String, dynamic>>> getReadings({
    int? teamId,
    String? category,
    DateTime? fromDate,
    DateTime? toDate,
  }) async {
    final params = <String, String>{};
    if (teamId != null) params['team_id'] = teamId.toString();
    if (category != null) params['category'] = category;
    if (fromDate != null) params['from_date'] = fromDate.toIso8601String();
    if (toDate != null) params['to_date'] = toDate.toIso8601String();

    final uri = Uri.parse('${client.baseUrl}/api/readings').replace(queryParameters: params.isEmpty ? null : params);
    final res = await client.getUri(uri);

    if (res.statusCode != 200) {
      throw Exception('Erro ao buscar leituras: ${res.body}');
    }
    final List data = jsonDecode(res.body);
    return data.cast<Map<String, dynamic>>();
  }

  Future<List<Map<String, dynamic>>> getSummary({
    int? teamId,
    DateTime? fromDate,
    DateTime? toDate,
  }) async {
    final params = <String, String>{};
    if (teamId != null) params['team_id'] = teamId.toString();
    if (fromDate != null) params['from_date'] = fromDate.toIso8601String();
    if (toDate != null) params['to_date'] = toDate.toIso8601String();

    final uri = Uri.parse('${client.baseUrl}/api/readings/summary').replace(queryParameters: params.isEmpty ? null : params);
    final res = await client.getUri(uri);

    if (res.statusCode != 200) {
      throw Exception('Erro ao buscar resumo: ${res.body}');
    }
    final List data = jsonDecode(res.body);
    return data.cast<Map<String, dynamic>>();
  }
}
