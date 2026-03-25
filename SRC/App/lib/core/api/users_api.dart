import 'dart:convert';
import 'api_client.dart';

class UsersApi {
  final ApiClient client;
  UsersApi(this.client);

  Future<List<Map<String, dynamic>>> getUsers() async {
    final response = await client.get('/api/users');

    if (response.statusCode == 200) {
      final List data = jsonDecode(response.body);
      return data.cast<Map<String, dynamic>>();
    }

    throw Exception('Erro ao buscar usuários: ${response.statusCode} - ${response.body}');
  }

  Future<Map<String, dynamic>> createUser({
    required String name,
    required String email,
    required String password,
    required String role,
    int? teamId,
    bool active = true,
  }) async {
    final response = await client.post('/api/users', body: {
      'name': name,
      'email': email,
      'password': password,
      'role': role,
      'team_id': teamId,
      'active': active,
    });

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }

    throw Exception('Erro ao criar usuário: ${response.statusCode} - ${response.body}');
  }

  Future<Map<String, dynamic>> updateUser({
    required int userId,
    String? name,
    String? email,
    String? password,
    String? role,
    int? teamId,
    bool? active,
  }) async {
    final response = await client.put('/api/users/$userId', body: {
      'name': name,
      'email': email,
      'password': password,
      'role': role,
      'team_id': teamId,
      'active': active,
    });

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }

    throw Exception('Erro ao atualizar usuário: ${response.statusCode} - ${response.body}');
  }

  Future<void> deleteUser(int userId) async {
    final response = await client.delete('/api/users/$userId');

    if (response.statusCode != 200) {
      throw Exception('Erro ao excluir usuário: ${response.statusCode} - ${response.body}');
    }
  }
}