// lib/data/models/status.dart
class Status {
  final String status; // "safe", "danger", atau "unknown"
  final int level;
  final String message;

  Status({required this.status, required this.level, required this.message});

  factory Status.fromJson(Map<String, dynamic> json) {
    return Status(
      status: json['status'],
      level: json['level'],
      message: json['message'],
    );
  }
}