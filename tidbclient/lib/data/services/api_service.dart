// mobile-flutter/lib/services/api_service.dart
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/alert.dart';
import '../models/status.dart';

class ApiService {
  // Gunakan IP 10.0.2.2 untuk emulator Android mengakses localhost PC
  final String _baseUrl = 'http://10.0.2.2:8000';

  Future<List<Alert>> fetchAlerts() async {
    final response = await http.get(Uri.parse('$_baseUrl/alerts/'));

    if (response.statusCode == 200) {
      List<dynamic> body = json.decode(response.body);
      List<Alert> alerts = body.map((dynamic item) => Alert.fromJson(item)).toList();
      return alerts;
    } else {
      throw Exception('Gagal memuat data alerts');
    }
  }

  Future<void> registerToken(String token) async {
    final url = Uri.parse('$_baseUrl/devices/register');
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'token': token}),
      );
      if (response.statusCode != 201) {
        // Jika gagal, lempar error agar bisa ditangkap oleh Repository/BLoC
        throw Exception('Gagal registrasi token. Status: ${response.statusCode}');
      }
      print('ApiService: Token berhasil dikirim ke server.');
    } catch (e) {
      // Lempar kembali error untuk ditangani di lapisan atasnya
      rethrow;
    }
  }

  Future<void> uploadReport(File imageFile, String notes) async {
    final url = Uri.parse('$_baseUrl/reports/');

    // Membuat request multi-bagian
    var request = http.MultipartRequest('POST', url);

    // Menambahkan file gambar
    request.files.add(
      await http.MultipartFile.fromPath(
        'image', // 'image' harus cocok dengan nama field di backend
        imageFile.path,
      ),
    );

    // Menambahkan data teks
    request.fields['notes'] = notes;

    try {
      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode != 201) {
        throw Exception('Gagal mengunggah laporan. Status: ${response.statusCode}');
      }
      print('ApiService: Laporan berhasil diunggah.');
    } catch (e) {
      rethrow;
    }
  }

  Future<Status> fetchLatestStatus() async {
    final response = await http.get(Uri.parse('$_baseUrl/status/latest'));
    if (response.statusCode == 200) {
      return Status.fromJson(json.decode(response.body));
    } else {
      throw Exception('Gagal memuat status terbaru');
    }
  }
}