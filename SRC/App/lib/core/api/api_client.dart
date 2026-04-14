import 'dart:convert';
import 'package:http/http.dart' as http;
import 'api_config.dart';

class ApiClient {
  final String baseUrl;
  String? _token;

  ApiClient({this.baseUrl = ApiConfig.baseUrl});

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

  Future<http.Response> getUri(Uri uri, {Map<String, String>? headers}) {
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

  Future<http.Response> put(
    String path, {
    Object? body,
    Map<String, String>? headers,
  }) {
    final uri = Uri.parse('$baseUrl$path');
    return http.put(
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