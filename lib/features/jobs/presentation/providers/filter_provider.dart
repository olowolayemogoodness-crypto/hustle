import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../discovery/data/job_model.dart';

class FilterNotifier extends Notifier<JobFilter> {
  @override
  JobFilter build() => JobFilter.nearby;

  void select(JobFilter filter) => state = filter;
}

final filterProvider =
    NotifierProvider<FilterNotifier, JobFilter>(FilterNotifier.new);

// View toggle: true = list, false = map
class ViewToggleNotifier extends Notifier<bool> {
  @override
  bool build() => true; // start on list view

  void toggleToMap() => state = false;
  void toggleToList() => state = true;
}


final viewToggleProvider =
    NotifierProvider<ViewToggleNotifier, bool>(ViewToggleNotifier.new);