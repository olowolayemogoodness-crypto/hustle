import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import 'package:hustle/core/utils/location_utils.dart';
import 'package:latlong2/latlong.dart';

import 'map_provider.dart';

class LocationNotifier extends AsyncNotifier<LatLng?> {
  @override
  Future<LatLng?> build() async {
    final position = await LocationUtils.getCurrentPosition();
    if (position == null) return null;

    final latLng = LatLng(position.latitude, position.longitude);

    // Push into map state immediately
    ref.read(mapProvider.notifier).updateUserPosition(latLng);
    return latLng;
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final position = await LocationUtils.getCurrentPosition();
      if (position == null) return null;
      final latLng = LatLng(position.latitude, position.longitude);
      ref.read(mapProvider.notifier).updateUserPosition(latLng);
      return latLng;
    });
  }
}

final locationProvider =
    AsyncNotifierProvider<LocationNotifier, LatLng?>(LocationNotifier.new);

// Stream-based live position updates
final positionStreamProvider = StreamProvider<LatLng>((ref) {
  return LocationUtils.positionStream().map(
    (p) => LatLng(p.latitude, p.longitude),
  );
});