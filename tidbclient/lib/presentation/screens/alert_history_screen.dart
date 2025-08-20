import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../bloc/alert/alert_bloc.dart';

class AlertHistoryScreen extends StatelessWidget {
  const AlertHistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Riwayat Peringatan AI'),
      ),
      body: BlocBuilder<AlertBloc, AlertState>(
        builder: (context, state) {
          if (state is AlertLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          if (state is AlertLoaded) {
            if (state.alerts.isEmpty) {
              return const Center(child: Text('Tidak ada riwayat peringatan.'));
            }
            return ListView.builder(
              itemCount: state.alerts.length,
              itemBuilder: (context, index) {
                final alert = state.alerts[index];
                return Card(
                  margin: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  child: ListTile(
                    leading: Icon(Icons.warning_amber_rounded, color: Colors.orange.shade800),
                    title: Text(
                      alert.reasoning,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: Text(
                      'Level ${alert.level} - ${alert.timestamp.toLocal()}',
                    ),
                  ),
                );
              },
            );
          }
          if (state is AlertError) {
            return Center(child: Text('Terjadi Error: ${state.message}'));
          }
          return const Center(child: Text('Silakan muat ulang data.'));
        },
      ),
    );
  }
}