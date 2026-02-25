import 'dart:convert';
import 'package:http/http.dart' as http;

import 'api_client.dart';

class AuthApi {
  final ApiClient client;
  AuthApi(this.client);

  Future<void> register({
    required String name,
    required String email,
    required String password,
    required String role, // operador/coordenador/admin
  }) async {
    final res = await client.post('/api/auth/register', body: {
      'name': name,
      'email': email,
      'password': password,
      'role': role,
    });

    if (res.statusCode != 200) {
      throw Exception(res.body);
    }

    final data = jsonDecode(res.body);
    await client.setToken(data['access_token']);
  }

  Future<void> login({
    required String email,
    required String password,
  }) async {
    final res = await client.post('/api/auth/login', body: {
      'email': email,
      'password': password,
    });

    if (res.statusCode != 200) {
      throw Exception(res.body);
    }

    final data = jsonDecode(res.body);
    await client.setToken(data['access_token']);
  }

  Future<Map<String, dynamic>> me() async {
    final http.Response res = await client.get('/api/auth/me');
    if (res.statusCode != 200) {
      throw Exception(res.body);
    }
    return jsonDecode(res.body);
  }
}