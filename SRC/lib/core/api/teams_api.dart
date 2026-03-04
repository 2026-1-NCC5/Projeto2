import 'dart:convert';
import 'api_client.dart';

class TeamsApi {
  final ApiClient client;
  TeamsApi(this.client);

  Future<List<Map<String, dynamic>>> getTeams() async {
    final response = await client.get('/teams');

    if (response.statusCode == 200) {
      final List data = jsonDecode(response.body);
      return data.cast<Map<String, dynamic>>();
    }
    throw Exception('Falha ao carregar equipes: ${response.statusCode} - ${response.body}');
  }

  Future<void> createTeam(String name) async {
    final response = await client.post(
      '/teams',
      body: {'name': name},
    );

    if (response.statusCode != 200 && response.statusCode != 201) {
      throw Exception('Erro ao criar equipe: ${response.statusCode} - ${response.body}');
    }
  }

  Future<void> deleteTeam(int id) async {
    final response = await client.delete('/teams/$id');

    if (response.statusCode != 200 && response.statusCode != 204) {
      throw Exception('Erro ao deletar equipe: ${response.statusCode} - ${response.body}');
    }
  }
}