import 'package:firebase_messaging/firebase_messaging.dart';
import '../../data/services/api_service.dart';

class NotificationRepository {
  final ApiService _apiService;
  final FirebaseMessaging _firebaseMessaging;

  NotificationRepository({
    ApiService? apiService,
    FirebaseMessaging? firebaseMessaging,
  })  : _apiService = apiService ?? ApiService(),
        _firebaseMessaging = firebaseMessaging ?? FirebaseMessaging.instance;

  Future<void> registerDevice() async {
    try {
      // 1. Minta izin
      await _firebaseMessaging.requestPermission();

      // 2. Dapatkan token
      final fcmToken = await _firebaseMessaging.getToken();

      // 3. Kirim ke server jika token ada
      if (fcmToken != null) {
        print("Token ditemukan, mendaftarkan ke server: $fcmToken");
        await _apiService.registerToken(fcmToken);
      } else {
        print("Gagal mendapatkan FCM Token untuk registrasi.");
      }
    } catch (e) {
      print("Error dalam proses registrasi perangkat: $e");
      // Di aplikasi produksi, kita akan menangani error ini lebih baik
      rethrow;
    }
  }
}