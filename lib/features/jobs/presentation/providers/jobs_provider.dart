import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/job_model.dart';

class JobsNotifier extends AsyncNotifier<List<JobListing>> {
  @override
  Future<List<JobListing>> build() async {
    // TODO: inject jobs_repository and call:
    // GET /api/v1/match/jobs?lat=...&lng=...&radius_km=5
    await Future.delayed(const Duration(milliseconds: 700));
    return JobListing.mockList();
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      await Future.delayed(const Duration(milliseconds: 700));
      return JobListing.mockList();
    });
  }

  Future<void> applyFilter(JobFilter filter) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final all = JobListing.mockList();
      switch (filter) {
        case JobFilter.nearby:
          return all..sort((a, b) => a.distanceKm.compareTo(b.distanceKm));
        case JobFilter.topPaying:
          return all..sort((a, b) => b.payKobo.compareTo(a.payKobo));
        case JobFilter.urgent:
          return all
              .where((j) =>
                  j.urgencyType == JobUrgencyType.todayOnly ||
                  (j.daysLeft != null && j.daysLeft! <= 2))
              .toList();
      }
    });
  }
}

final jobsProvider =
    AsyncNotifierProvider<JobsNotifier, List<JobListing>>(JobsNotifier.new);