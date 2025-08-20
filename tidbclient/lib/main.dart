import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:tidbclient/presentation/bloc/alert/alert_bloc.dart';
import 'package:tidbclient/presentation/bloc/notification/notification_bloc.dart';
import 'package:tidbclient/presentation/screens/alert_history_screen.dart';

// Anda perlu menambahkan file firebase_options.dart setelah konfigurasi
// (FlutterFire CLI akan membuatnya untuk Anda, atau Anda bisa melakukannya manual)
import 'domain/repositories/alert_repository.dart';
import 'domain/repositories/notification_repository.dart';
import 'firebase_options.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    // Menyediakan instance Repository dan BLoC ke seluruh widget tree
    return MultiRepositoryProvider(
      providers: [
        RepositoryProvider(create: (context) => AlertRepository()),
        RepositoryProvider(create: (context) => NotificationRepository()),
      ],
      // Kemudian menyediakan SEMUA BLoC
      child: MultiBlocProvider(
        providers: [
          BlocProvider(
            lazy: false,
            create: (context) => AlertBloc(
              alertRepository: context.read<AlertRepository>(),
            )..add(FetchAlerts()), // Memuat data alert
          ),
          BlocProvider(
            lazy: false,
            create: (context) => NotificationBloc(
              notificationRepository: context.read<NotificationRepository>(),
            )..add(RegisterDevice()), // Memicu registrasi perangkat
          ),
        ],
        child: MaterialApp(
          title: 'Agen Lingkungan',
          theme: ThemeData(
            primarySwatch: Colors.indigo,
            visualDensity: VisualDensity.adaptivePlatformDensity,
          ),
          home: const AlertHistoryScreen(),
        ),
      ),
    );
  }
}