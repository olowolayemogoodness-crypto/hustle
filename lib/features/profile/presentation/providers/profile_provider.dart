// lib/features/profile/presentation/providers/profile_provider.dart

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hustle/core/network/dio_client.dart';
import 'package:hustle/features/profile/data/models/profile_model.dart';
// lib/features/profile/presentation/providers/profile_provider.dart

class ProfileNotifier extends AsyncNotifier<WorkerProfile> {
  @override
  Future<WorkerProfile> build() async {
    return _fetch();
  }

  Future<WorkerProfile> _fetch() async {
    try {
      final meResp = await DioClient.instance.get('/api/v1/auth/me');
      final userId = meResp.data['id'] as String;

      final results = await Future.wait([
        DioClient.instance.get('/api/v1/profile/worker'),
        DioClient.instance.get('/api/v1/ratings/$userId'),
      ]);

      final profile = WorkerProfile.fromBackend(
        results[0].data as Map<String, dynamic>,
      );

      // Attach real reviews
      final ratingsData = results[1].data['data'] as List? ?? [];
      final reviews = ratingsData.map((r) {
        final m = r as Map<String, dynamic>;
        return WorkerReview(
          id:                 m['id'] as String,
          reviewerName:       m['rater_id'] as String? ?? 'Employer',
          reviewerAvatarUrl:  null,
          rating:             (m['score'] as num).toDouble(),
          comment:            m['comment'] as String? ?? '',
          date:               DateTime.parse(m['created_at'] as String),
        );
      }).toList();

      return WorkerProfile(
        id:             profile.id,
        fullName:       profile.fullName,
        avatarUrl:      profile.avatarUrl,
        skills:         profile.skills,
        primarySkills:  profile.primarySkills,
        location:       profile.location,
        joinedAt:       profile.joinedAt,
        totalJobs:      profile.totalJobs,
        trustScore:     profile.trustScore,
        completionRate: profile.completionRate,
        disputesCount:  profile.disputesCount,
        ratingsCount:   reviews.length,
        isVerified:     profile.isVerified,
        topPercentile:  profile.topPercentile,
        reviews:        reviews,
      );

    } catch (e) {
      debugPrint('Profile fetch error: $e');
      return WorkerProfile.mock();
    }
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(_fetch);
  }
}

final profileProvider =
    AsyncNotifierProvider<ProfileNotifier, WorkerProfile>(ProfileNotifier.new);