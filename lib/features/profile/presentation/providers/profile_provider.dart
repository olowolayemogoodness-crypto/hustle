// lib/features/profile/presentation/providers/profile_provider.dart

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hustle/core/network/dio_client.dart';
import 'package:hustle/features/profile/data/models/profile_model.dart';
// lib/features/profile/presentation/providers/profile_provider.dart

class ProfileNotifier extends AsyncNotifier<WorkerProfile> {
  @override
  Future<WorkerProfile> build() async {
    try {
      final response = await DioClient.instance.get(
        '/api/v1/profile/worker',
      );
      return WorkerProfile.fromBackend(
        response.data as Map<String, dynamic>,
      );
    } catch (_) {
      return WorkerProfile.mock();
    }
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final response = await DioClient.instance.get('/api/v1/profile/worker');
      return WorkerProfile.fromBackend(
        response.data as Map<String, dynamic>,
      );
    });
  }
}

final profileProvider =
    AsyncNotifierProvider<ProfileNotifier, WorkerProfile>(ProfileNotifier.new);