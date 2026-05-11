import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/profile_model.dart';

class ProfileNotifier extends AsyncNotifier<WorkerProfile> {
  @override
  Future<WorkerProfile> build() async {
    // TODO: replace with real API call via profile_repository
    await Future.delayed(const Duration(milliseconds: 500));
    return WorkerProfile.mock();
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      await Future.delayed(const Duration(milliseconds: 500));
      return WorkerProfile.mock();
    });
  }
}

final profileProvider =
    AsyncNotifierProvider<ProfileNotifier, WorkerProfile>(ProfileNotifier.new);