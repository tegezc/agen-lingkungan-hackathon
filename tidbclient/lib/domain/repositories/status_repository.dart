// lib/domain/repositories/status_repository.dart
import '../../data/models/status.dart';
import '../../data/services/api_service.dart';

class StatusRepository {
  final ApiService _apiService;

  StatusRepository({ApiService? apiService})
      : _apiService = apiService ?? ApiService();

  Future<Status> getLatestStatus() async {
    return await _apiService.fetchLatestStatus();
  }
}