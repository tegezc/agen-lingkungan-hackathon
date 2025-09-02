part of 'status_bloc.dart';

abstract class StatusState extends Equatable {
  const StatusState();
  @override List<Object> get props => [];
}
class StatusInitial extends StatusState {}
class StatusLoading extends StatusState {}
class StatusLoaded extends StatusState {
  final Status status;
  const StatusLoaded(this.status);
  @override List<Object> get props => [status];
}
class StatusError extends StatusState {
  final String message;
  const StatusError(this.message);
  @override List<Object> get props => [message];
}