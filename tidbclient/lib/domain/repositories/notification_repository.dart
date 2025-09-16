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
      // 1. Request permission
      await _firebaseMessaging.requestPermission();

      // 2. Get the token
      final fcmToken = await _firebaseMessaging.getToken();

      // 3. Send to the server if the token exists
      if (fcmToken != null) {
         print("Token found, registering to server: $fcmToken");
        await _apiService.registerToken(fcmToken);
      } else {
        print("Failed to get FCM Token for registration.");
      }
    } catch (e) {
     print("Error during the device registration process: $e");
       // In a production app, we would handle this error better
      rethrow;
    }
  }
}