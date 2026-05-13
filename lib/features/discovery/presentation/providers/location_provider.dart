import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hustle/core/utils/location_utils.dart';
import 'package:latlong2/latlong.dart';
import 'map_provider.dart';

class LocationNotifier extends AsyncNotifier<LatLng?> {
  @override
  Future<LatLng?> build() async {
    // Get initial position
    final position = await LocationUtils.getCurrentPosition();
    if (position == null) return null;

    final latLng = LatLng(position.latitude, position.longitude);
    ref.read(mapProvider.notifier).updateUserPosition(latLng);

    // ← Start live stream from here, not from the screen
    ref.listen(positionStreamProvider, (_, next) {
      next.whenData((latlng) {
        ref.read(mapProvider.notifier).updateUserPosition(latlng);
      });
    });

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

final positionStreamProvider = StreamProvider<LatLng>((ref) {
  return LocationUtils.positionStream()
      .map((p) => LatLng(p.latitude, p.longitude));
});