import '../../data/models/alert.dart';
import '../../data/services/api_service.dart';

class AlertRepository {
  final ApiService _apiService;

  AlertRepository({ApiService? apiService})
      : _apiService = apiService ?? ApiService();

  Future<List<Alert>> getAlerts() async {
    try {
      return await _apiService.fetchAlerts();
    } catch (e) {
      rethrow;
    }
  }
}