// mobile-flutter/lib/services/api_service.dart
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/alert.dart';
import '../models/status.dart';

class ApiService {
  final String _baseUrl = 'https://floodcast-service-669250331086.asia-southeast2.run.app';

  Future<List<Alert>> fetchAlerts() async {
    final response = await http.get(Uri.parse('$_baseUrl/alerts/alerts'));

    if (response.statusCode == 200) {
      List<dynamic> body = json.decode(response.body);
      List<Alert> alerts = body.map((dynamic item) => Alert.fromJson(item)).toList();
      return alerts;
    } else {
      throw Exception('Failed to load alerts data');
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
         // If it fails, throw an error so it can be caught by the Repository/BLoC
        throw Exception('Gagal registrasi token. Status: ${response.statusCode}');
      }
      print('ApiService: Token successfully sent to the server.');
    } catch (e) {
     // Rethrow the error to be handled in the upper layer
      rethrow;
    }
  }

  Future<void> uploadReport(File imageFile, String notes) async {
    final url = Uri.parse('$_baseUrl/reports/');

    // Create a multipart request
    var request = http.MultipartRequest('POST', url);

     // Add the image file
    request.files.add(
      await http.MultipartFile.fromPath(
        'image', // 'image' harus cocok dengan nama field di backend
        imageFile.path,
      ),
    );

     // Add the text data
    request.fields['notes'] = notes;

    try {
      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode != 201) {
        throw Exception('Failed to upload report. Status: ${response.statusCode}');
      }
      print('ApiService: Report uploaded successfully.');
    } catch (e) {
      rethrow;
    }
  }

  Future<Status> fetchLatestStatus() async {
    final response = await http.get(Uri.parse('$_baseUrl/status/latest'));
    if (response.statusCode == 200) {
      return Status.fromJson(json.decode(response.body));
    } else {
      throw Exception('Failed to load latest status');
    }
  }
}