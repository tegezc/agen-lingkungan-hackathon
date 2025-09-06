import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../bloc/status/status_bloc.dart';
import 'alert_history_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // Tentukan warna dan ikon berdasarkan status
    Color statusColor = Colors.grey;
    IconData statusIcon = Icons.help_outline;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Environment Status'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            BlocBuilder<StatusBloc, StatusState>(
              builder: (context, state) {
                String statusText = "Loading Status...";
                String messageText = "Contacting server...";

                if (state is StatusLoaded) {
                  statusText = state.status.status.toUpperCase();
                  messageText = state.status.message;
                  if (state.status.status == 'safe') {
                    statusColor = Colors.green.shade700;
                    statusIcon = Icons.check_circle_outline;
                  } else if (state.status.status == 'danger') {
                    statusColor = Colors.red.shade700;
                    statusIcon = Icons.warning_amber_rounded;
                  }
                } else if (state is StatusError) {
                  statusText = "ERROR";
                  messageText = state.message;
                  statusColor = Colors.grey.shade700;
                  statusIcon = Icons.error_outline;
                }

                return Card(
                  color: statusColor,
                  elevation: 6,
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Icon(statusIcon, color: Colors.white, size: 48),
                        const SizedBox(height: 16),
                        Text(
                          statusText,
                          style: const TextStyle(color: Colors.white, fontSize: 32, fontWeight: FontWeight.bold),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          messageText,
                          style: const TextStyle(color: Colors.white, fontSize: 16),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
            const Spacer(),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                icon: const Icon(Icons.history),
                label: const Text('View Alert History'),
                onPressed: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(builder: (context) => const AlertHistoryScreen()),
                  );
                },
                style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
              ),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }
}