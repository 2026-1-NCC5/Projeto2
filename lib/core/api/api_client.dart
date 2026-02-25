import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

import 'api_config.dart';

class ApiClient {
  final _storage = const FlutterSecureStorage();

  Future<String?> getToken() => _storage.read(key: 'token');
  Future<void> setToken(String token) => _storage.write(key: 'token', value: token);
  Future<void> clearToken() => _storage.delete(key: 'token');

  Uri _uri(String path, [Map<String, String>? q]) {
    return Uri.parse('${ApiConfig.baseUrl}$path').replace(queryParameters: q);
  }

  Future<http.Response> get(String path, {Map<String, String>? query}) async {
    final token = await getToken();
    return http.get(
      _uri(path, query),
      headers: {
        'Content-Type': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      },
    );
  }

  Future<http.Response> post(String path, {Object? body}) async {
    final token = await getToken();
    return http.post(
      _uri(path),
      headers: {
        'Content-Type': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      },
      body: jsonEncode(body),
    );
  }
}