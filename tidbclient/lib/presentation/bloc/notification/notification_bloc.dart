import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../domain/repositories/notification_repository.dart';

part 'notification_event.dart';
part 'notification_state.dart';

class NotificationBloc extends Bloc<NotificationEvent, NotificationState> {
  final NotificationRepository _notificationRepository;

  NotificationBloc({required NotificationRepository notificationRepository})
      : _notificationRepository = notificationRepository,
        super(NotificationInitial()) {
    on<RegisterDevice>(_onRegisterDevice);
  }

  void _onRegisterDevice(RegisterDevice event, Emitter<NotificationState> emit) async {
    emit(DeviceRegistrationInProgress());
    try {
      await _notificationRepository.registerDevice();
      emit(DeviceRegistrationSuccess());
    } catch (e) {
      emit(DeviceRegistrationFailure(e.toString()));
    }
  }
}