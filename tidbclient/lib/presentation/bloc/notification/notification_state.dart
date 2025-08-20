part of 'notification_bloc.dart';

abstract class NotificationState extends Equatable {
  const NotificationState();
  @override
  List<Object> get props => [];
}

class NotificationInitial extends NotificationState {}
class DeviceRegistrationInProgress extends NotificationState {}
class DeviceRegistrationSuccess extends NotificationState {}
class DeviceRegistrationFailure extends NotificationState {
  final String error;
  const DeviceRegistrationFailure(this.error);
  @override
  List<Object> get props => [error];
}