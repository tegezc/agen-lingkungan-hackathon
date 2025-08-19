// mobile-flutter/lib/models/alert.dart
class Alert {
  final DateTime timestamp;
  final String reasoning;
  final int level;

  Alert({
    required this.timestamp,
    required this.reasoning,
    required this.level,
  });

  factory Alert.fromJson(Map<String, dynamic> json) {
    return Alert(
      timestamp: DateTime.parse(json['timestamp']),
      reasoning: json['reasoning'],
      level: json['level'],
    );
  }
}