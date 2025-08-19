import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:tidbclient/presentation/bloc/alert_bloc.dart';
import 'package:tidbclient/presentation/screens/alert_history_screen.dart';

// Anda perlu menambahkan file firebase_options.dart setelah konfigurasi
// (FlutterFire CLI akan membuatnya untuk Anda, atau Anda bisa melakukannya manual)
import 'domain/repositories/alert_repository.dart';
import 'firebase_options.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

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
    return RepositoryProvider(
      create: (context) => AlertRepository(),
      child: BlocProvider(
        create: (context) => AlertBloc(
          alertRepository: RepositoryProvider.of<AlertRepository>(context),
        )..add(FetchAlerts()), // Langsung panggil event pertama kali
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