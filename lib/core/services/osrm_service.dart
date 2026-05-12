import 'package:dio/dio.dart';
import 'package:latlong2/latlong.dart';
import '../config/app_config.dart';

class OsrmRoute {
  const OsrmRoute({
    required this.distanceMetres,
    required this.durationSeconds,
    required this.polylinePoints,
  });

  final double distanceMetres;
  final double durationSeconds;
  final List<LatLng> polylinePoints;

  String get distanceDisplay {
    if (distanceMetres < 1000) {
      return '${distanceMetres.toInt()}m';
    }
    return '${(distanceMetres / 1000).toStringAsFixed(1)}km';
  }

  String get durationDisplay {
    final mins = (durationSeconds / 60).ceil();
    return mins < 60 ? '${mins}min' : '${(mins / 60).toStringAsFixed(1)}hr';
  }
}

class OsrmService {
  OsrmService._();

  static final _dio = Dio(BaseOptions(
    baseUrl: AppConfig.osrmBaseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
  ));

  /// Get route between two points using OSRM (OSM-based, free)
  /// Deploy your own instance on Render for production:
  /// https://hub.docker.com/r/osrm/osrm-backend
  static Future<OsrmRoute?> getRoute({
    required LatLng origin,
    required LatLng destination,
    String profile = 'driving', // driving | cycling | foot
  }) async {
    try {
      final coords =
          '${origin.longitude},${origin.latitude};${destination.longitude},${destination.latitude}';

      final response = await _dio.get<Map>(
        '/$profile/$coords',
        queryParameters: {
          'overview': 'full',
          'geometries': 'geojson',
          'steps': false,
        },
      );

      final routes = response.data?['routes'] as List?;
      if (routes == null || routes.isEmpty) return null;

      final route = routes.first as Map;
      final geometry = route['geometry'] as Map;
      final coordinates = geometry['coordinates'] as List;

      final points = coordinates.map((c) {
        final coord = c as List;
        return LatLng(coord[1] as double, coord[0] as double);
      }).toList();

      return OsrmRoute(
        distanceMetres: (route['distance'] as num).toDouble(),
        durationSeconds: (route['duration'] as num).toDouble(),
        polylinePoints: points,
      );
    } catch (_) {
      return null;
    }
  }
}