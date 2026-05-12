import 'package:dio/dio.dart';
import '../config/app_config.dart';

class NominatimResult {
  const NominatimResult({
    required this.displayName,
    required this.latitude,
    required this.longitude,
  });

  final String displayName;
  final double latitude;
  final double longitude;
}

class NominatimService {
  NominatimService._();

  static final _dio = Dio(BaseOptions(
    baseUrl: AppConfig.nominatimBaseUrl,
    headers: {
      // Required by Nominatim usage policy
      'User-Agent': 'LocGig/1.0 (hello@locgig.app)',
      'Accept-Language': 'en',
    },
    connectTimeout: const Duration(seconds: 8),
    receiveTimeout: const Duration(seconds: 8),
  ));

  /// Geocode a query string to coordinates — Nigeria-scoped
  static Future<List<NominatimResult>> search(String query) async {
    try {
      final response = await _dio.get<List>('/search', queryParameters: {
        'q': query,
        'format': 'json',
        'countrycodes': 'ng',   // restrict to Nigeria
        'limit': 5,
        'addressdetails': 1,
      });

      return (response.data ?? []).map((item) {
        return NominatimResult(
          displayName: item['display_name'] as String,
          latitude: double.parse(item['lat'] as String),
          longitude: double.parse(item['lon'] as String),
        );
      }).toList();
    } catch (_) {
      return [];
    }
  }

  /// Reverse geocode coordinates to an address
  static Future<String?> reverse(double lat, double lng) async {
    try {
      final response = await _dio.get<Map>('/reverse', queryParameters: {
        'lat': lat,
        'lon': lng,
        'format': 'json',
        'zoom': 14,
      });
      return response.data?['display_name'] as String?;
    } catch (_) {
      return null;
    }
  }
}