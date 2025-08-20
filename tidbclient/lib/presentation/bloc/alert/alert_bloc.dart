import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:equatable/equatable.dart';
import '../../../data/models/alert.dart';
import '../../../domain/repositories/alert_repository.dart';

part 'alert_event.dart';
part 'alert_state.dart';

class AlertBloc extends Bloc<AlertEvent, AlertState> {
  final AlertRepository _alertRepository;

  AlertBloc({required AlertRepository alertRepository})
      : _alertRepository = alertRepository,
        super(AlertInitial()) {
    on<FetchAlerts>(_onFetchAlerts);
  }

  void _onFetchAlerts(FetchAlerts event, Emitter<AlertState> emit) async {
    emit(AlertLoading());
    try {
      final alerts = await _alertRepository.getAlerts();
      emit(AlertLoaded(alerts));
    } catch (e) {
      emit(AlertError(e.toString()));
    }
  }
}