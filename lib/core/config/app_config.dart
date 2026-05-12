class AppConfig {
  AppConfig._();

  static const String apiBaseUrl = String.fromEnvironment(
    'API_URL',
    defaultValue: 'https://api.locgig.app/api/v1',
  );

  // MapTiler free tier — 100K tiles/month, no credit card
  // Get key at: https://cloud.maptiler.com/account/keys
  static const String mapTilerKey = String.fromEnvironment(
    'MAPTILER_KEY',
    defaultValue: '',
  );

  // OSRM public instance for MVP — deploy your own on Render for prod
  static const String osrmBaseUrl =
      'https://router.project-osrm.org/route/v1';

  // Nominatim — free, OSM-backed, no key needed
  static const String nominatimBaseUrl =
      'https://nominatim.openstreetmap.org';

  // MapTiler Streets tile URL — clean, offline-cacheable
  // Falls back to raw OSM if no key provided (rate limited publicly)
  static String get tileUrlTemplate {
    if (mapTilerKey.isNotEmpty) {
      return 'https://api.maptiler.com/maps/streets/{z}/{x}/{y}.png?key=$mapTilerKey';
    }
    return 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
  }

  static const bool isDev =
      String.fromEnvironment('FLUTTER_APP_ENV', defaultValue: 'dev') == 'dev';
}