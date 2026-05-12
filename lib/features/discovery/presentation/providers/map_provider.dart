import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:latlong2/latlong.dart';
// Lagos Mainland default camera — used before GPS resolves
const kDefaultLagosCenter = LatLng(6.5244, 3.3792);
const kDefaultZoom = 14.0;

class MapState {
  const MapState({
    this.selectedJobId,
    this.userPosition,
    this.cameraPosition = kDefaultLagosCenter,
    this.zoom = kDefaultZoom,
    this.isFollowingUser = true,
  });

  final String? selectedJobId;
  final LatLng? userPosition;
  final LatLng cameraPosition;
  final double zoom;
  final bool isFollowingUser;

  MapState copyWith({
    String? selectedJobId,
    LatLng? userPosition,
    LatLng? cameraPosition,
    double? zoom,
    bool? isFollowingUser,
    bool clearSelection = false,
  }) {
    return MapState(
      selectedJobId: clearSelection ? null : (selectedJobId ?? this.selectedJobId),
      userPosition: userPosition ?? this.userPosition,
      cameraPosition: cameraPosition ?? this.cameraPosition,
      zoom: zoom ?? this.zoom,
      isFollowingUser: isFollowingUser ?? this.isFollowingUser,
    );
  }
}

class MapNotifier extends Notifier<MapState> {
  @override
  MapState build() => const MapState();

  void selectJob(String jobId) {
    state = state.copyWith(selectedJobId: jobId);
  }

  void clearSelection() {
    state = state.copyWith(clearSelection: true);
  }

  void updateUserPosition(LatLng position) {
    state = state.copyWith(
      userPosition: position,
      cameraPosition: state.isFollowingUser ? position : state.cameraPosition,
    );
  }

  void stopFollowingUser() {
    state = state.copyWith(isFollowingUser: false);
  }

  void recenterOnUser() {
    if (state.userPosition != null) {
      state = state.copyWith(
        cameraPosition: state.userPosition,
        isFollowingUser: true,
      );
    }
  }
}

final mapProvider = NotifierProvider<MapNotifier, MapState>(MapNotifier.new);