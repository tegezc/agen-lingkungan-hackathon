import '../../data/models/alert.dart';
import '../../data/services/api_service.dart';

class AlertRepository {
  final ApiService _apiService;

  AlertRepository({ApiService? apiService})
      : _apiService = apiService ?? ApiService();

  Future<List<Alert>> getAlerts() async {
    try {
      // Meneruskan panggilan ke lapisan data
      return await _apiService.fetchAlerts();
    } catch (e) {
      // Di aplikasi produksi, di sini kita akan melakukan error logging
      // dan bisa menggunakan 'Either' seperti di proyek Anda sebelumnya.
      // Untuk kecepatan hackathon, kita re-throw error-nya.
      rethrow;
    }
  }
}