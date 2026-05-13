// lib/core/services/nominatim_service.dart
import 'package:dio/dio.dart';
import 'package:latlong2/latlong.dart';
import '../config/app_config.dart';

class NominatimResult {
  const NominatimResult({required this.displayName, required this.latLng});
  final String displayName;
  final LatLng latLng;
}

class NominatimService {
  NominatimService._();

  static final _dio = Dio(BaseOptions(
    baseUrl: AppConfig.nominatimBaseUrl,
    headers: {'User-Agent': 'HustleApp/1.0'},
  ));

  static Future<List<NominatimResult>> search(String query) async {
    if (query.trim().isEmpty) return [];
    try {
      final response = await _dio.get<List>('/search', queryParameters: {
        'q': '$query, Lagos, Nigeria', // ← bias to Lagos for MVP
        'format': 'json',
        'limit': 5,
      });

      return (response.data ?? []).map((item) {
        return NominatimResult(
          displayName: item['display_name'] as String,
          latLng: LatLng(
            double.parse(item['lat'] as String),
            double.parse(item['lon'] as String),
          ),
        );
      }).toList();
    } catch (_) {
      return [];
    }
  }
}