import 'dart:convert';
import 'api_client.dart';

class GoalsApi {
  final ApiClient client;
  GoalsApi(this.client);

  Future<List<Map<String, dynamic>>> getGoals({int? teamId}) async {
    final params = teamId != null ? {'team_id': teamId.toString()} : null;
    final uri = Uri.parse('${client.baseUrl}/api/goals').replace(queryParameters: params);
    final res = await client.getUri(uri);

    if (res.statusCode != 200) {
      throw Exception('Erro ao buscar metas: ${res.body}');
    }
    final List data = jsonDecode(res.body);
    return data.cast<Map<String, dynamic>>();
  }

  Future<Map<String, dynamic>> upsertGoal({
    required int teamId,
    required String category,
    required double targetKg,
  }) async {
    final res = await client.post('/api/goals', body: {
      'team_id': teamId,
      'category': category,
      'target_kg': targetKg,
    });
    if (res.statusCode != 200) {
      throw Exception('Erro ao salvar meta: ${res.body}');
    }
    return jsonDecode(res.body);
  }

  Future<void> deleteGoal(int goalId) async {
    final res = await client.delete('/api/goals/$goalId');
    if (res.statusCode != 200) {
      throw Exception('Erro ao remover meta: ${res.body}');
    }
  }
}
