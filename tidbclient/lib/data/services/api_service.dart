// mobile-flutter/lib/services/api_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/alert.dart';

class ApiService {
  // Gunakan IP 10.0.2.2 untuk emulator Android mengakses localhost PC
  final String _baseUrl = 'http://10.0.2.2:8000';

  Future<List<Alert>> fetchAlerts() async {
    final response = await http.get(Uri.parse('$_baseUrl/alerts/alerts'));

    if (response.statusCode == 200) {
      List<dynamic> body = json.decode(response.body);
      List<Alert> alerts = body.map((dynamic item) => Alert.fromJson(item)).toList();
      return alerts;
    } else {
      throw Exception('Gagal memuat data alerts');
    }
  }
}