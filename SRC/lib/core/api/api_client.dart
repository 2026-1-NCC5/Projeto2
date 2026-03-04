import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiClient {
  // Troque para o IP da sua máquina se testar no celular:
  // Android emulator: http://10.0.2.2:8000
  // Celular físico:   http://SEU_IP:8000
  final String baseUrl;

  String? _token;

  ApiClient({this.baseUrl = 'http://10.0.2.2:8000'});

  void setToken(String? token) => _token = token;

  Map<String, String> _defaultHeaders([Map<String, String>? headers]) {
    final h = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    if (_token != null && _token!.isNotEmpty) {
      h['Authorization'] = 'Bearer $_token';
    }

    if (headers != null) h.addAll(headers);
    return h;
  }

  Future<http.Response> get(String path, {Map<String, String>? headers}) {
    final uri = Uri.parse('$baseUrl$path');
    return http.get(uri, headers: _defaultHeaders(headers));
  }

  Future<http.Response> post(
    String path, {
    Object? body,
    Map<String, String>? headers,
  }) {
    final uri = Uri.parse('$baseUrl$path');
    return http.post(
      uri,
      headers: _defaultHeaders(headers),
      body: body == null ? null : (body is String ? body : jsonEncode(body)),
    );
    }

  Future<http.Response> delete(String path, {Map<String, String>? headers}) {
    final uri = Uri.parse('$baseUrl$path');
    return http.delete(uri, headers: _defaultHeaders(headers));
  }
}