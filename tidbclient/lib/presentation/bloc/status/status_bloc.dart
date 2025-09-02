import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../data/models/status.dart';
import '../../../domain/repositories/status_repository.dart';

part 'status_event.dart';
part 'status_state.dart';

class StatusBloc extends Bloc<StatusEvent, StatusState> {
  final StatusRepository _statusRepository;

  StatusBloc({required StatusRepository statusRepository})
      : _statusRepository = statusRepository,
        super(StatusInitial()) {
    on<FetchStatus>(_onFetchStatus);
  }

  void _onFetchStatus(FetchStatus event, Emitter<StatusState> emit) async {
    emit(StatusLoading());
    try {
      final status = await _statusRepository.getLatestStatus();
      emit(StatusLoaded(status));
    } catch (e) {
      emit(StatusError(e.toString()));
    }
  }
}