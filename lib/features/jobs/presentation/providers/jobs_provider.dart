// lib/features/discovery/presentation/providers/jobs_provider.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hustle/core/network/dio_client.dart';
import 'package:hustle/features/discovery/data/job_model.dart';
import 'package:hustle/features/discovery/presentation/providers/location_provider.dart';



class JobsNotifier extends AsyncNotifier<List<JobListing>> {
  @override
  Future<List<JobListing>> build() async {
    return _fetchJobs();
  }

  Future<List<JobListing>> _fetchJobs() async {
    final location = ref.read(locationProvider).value;

    try {
      final response = await DioClient.instance.get(
        '/api/v1/jobs/nearby',
        queryParameters: {
          'lat':       location?.latitude  ?? 6.5244,
          'lng':       location?.longitude ?? 3.3792,
          'radius_km': 10,
          'limit':     20,
        },
      );
      final data = response.data['data'] as List;
      return data
          .map((j) => JobListing.fromBackend(j as Map<String, dynamic>))
          .toList();
    } catch (_) {
      return JobListing.mockList();
    }
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(_fetchJobs);
  }

  Future<void> applyFilter(JobFilter filter) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final jobs = await _fetchJobs();
      switch (filter) {
        case JobFilter.nearby:
          return jobs..sort((a, b) =>
              a.distanceKm.compareTo(b.distanceKm));
        case JobFilter.topPaying:
          return jobs..sort((a, b) =>
              b.payKobo.compareTo(a.payKobo));
        case JobFilter.urgent:
          return jobs.where((j) =>
              j.urgencyType == JobUrgencyType.todayOnly ||
              (j.daysLeft != null && j.daysLeft! <= 2)).toList();
      }
    });
  }
}

final jobsProvider =
    AsyncNotifierProvider<JobsNotifier, List<JobListing>>(JobsNotifier.new);