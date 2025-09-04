import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:tidbclient/presentation/screens/report_screen.dart';
import '../bloc/alert/alert_bloc.dart';
import 'alert_detail_screen.dart';

class AlertHistoryScreen extends StatelessWidget {
  const AlertHistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Riwayat Peringatan AI'),
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          // Memanggil event untuk memuat ulang data saat ditarik
          context.read<AlertBloc>().add(FetchAlerts());
        },
        child: BlocBuilder<AlertBloc, AlertState>(
          builder: (context, state) {
            if (state is AlertLoading) {
              return const Center(child: CircularProgressIndicator());
            }
            if (state is AlertLoaded) {
              if (state.alerts.isEmpty) {
                return const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.shield_outlined, size: 80, color: Colors.grey),
                      SizedBox(height: 16),
                      Text(
                        'Tidak Ada Peringatan Saat Ini',
                        style: TextStyle(fontSize: 18, color: Colors.grey),
                      ),
                    ],
                  ),
                );
              }
              return ListView.builder(
                itemCount: state.alerts.length,
                itemBuilder: (context, index) {
                  final alert = state.alerts[index];
                  return Card(
                    margin: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    elevation: 3,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: InkWell( // Membuat kartu bisa diklik
                      onTap: () {
                        Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (context) => AlertDetailScreen(alert: alert),
                          ),
                        );
                      },
                      child: Container(
                        decoration: BoxDecoration(
                            border: Border(left: BorderSide(color: alert.level >= 3 ? Colors.red.shade400 : Colors.orange.shade400, width: 5)),
                            borderRadius: BorderRadius.circular(10)
                        ),
                        child: ListTile(
                          title: Text(
                            alert.reasoning,
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          subtitle: Text(
                            'Level ${alert.level} - ${alert.timestamp.toLocal()}',
                          ),
                          trailing: const Icon(Icons.chevron_right, color: Colors.grey),
                        ),
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
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          Navigator.of(context).push(
            MaterialPageRoute(builder: (context) => const ReportScreen()),
          );
        },
        icon: const Icon(Icons.camera_alt),
        label: const Text('Lapor Banjir'),
      ),
    );
  }
}