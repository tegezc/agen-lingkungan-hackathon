import 'package:flutter/material.dart';
import '../../data/models/alert.dart';

class AlertDetailScreen extends StatelessWidget {
  final Alert alert;

  const AlertDetailScreen({super.key, required this.alert});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Alert Details'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Alert Level ${alert.level}',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: alert.level >= 3 ? Colors.red.shade700 : Colors.orange.shade800,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Time: ${alert.timestamp.toLocal()}',
              style: const TextStyle(fontSize: 16, color: Colors.grey),
            ),
            const Divider(height: 32),
            const Text(
              'Reasoning & Analysis from AI:',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Text(
              alert.reasoning,
              style: const TextStyle(fontSize: 16, height: 1.5),
            ),
          ],
        ),
      ),
    );
  }
}