import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

// Anda perlu menambahkan file firebase_options.dart setelah konfigurasi
// (FlutterFire CLI akan membuatnya untuk Anda, atau Anda bisa melakukannya manual)
import 'firebase_options.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {

  @override
  void initState() {
    super.initState();
    setupFcm();
  }

  void setupFcm() async {
    // Meminta izin notifikasi dari pengguna
    await FirebaseMessaging.instance.requestPermission();

    // Mengambil token unik untuk perangkat ini
    final fcmToken = await FirebaseMessaging.instance.getToken();

    // Print token ini ke konsol. KITA SANGAT MEMBUTUHKAN TOKEN INI UNTUK TESTING!
    print("====================================");
    print("FCM Token: $fcmToken");
    print("====================================");

    // Mendengarkan notifikasi yang masuk saat aplikasi terbuka
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      print('Pesan diterima selagi aplikasi terbuka!');
      if (message.notification != null) {
        print('Pesan berisi notifikasi: ${message.notification}');
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: const Text('Agen Lingkungan')),
        body: const Center(child: Text('Aplikasi siap menerima notifikasi.')),
      ),
    );
  }
}