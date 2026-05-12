import '../env.dart';

class AppConfig {
  AppConfig._();

  static String get apiBaseUrl     => Env.apiBaseUrl;
  static String get mapTilerKey    => Env.mapTilerKey;
  static String get termiiApiKey   => Env.termiiApiKey;
  static String get termiiSenderId => Env.termiiSenderId;

  // OSRM public instance for MVP — deploy your own on Render for prod
  static const String osrmBaseUrl =
      'https://router.project-osrm.org/route/v1';

  // Nominatim — free, OSM-backed, no key needed
  static const String nominatimBaseUrl =
      'https://nominatim.openstreetmap.org';

  static String get tileUrlTemplate {
    final key = Env.mapTilerKey;
    return key.isNotEmpty
        ? 'https://api.maptiler.com/maps/streets/{z}/{x}/{y}.png?key=$key'
        : 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
  }

  static const bool isDev = bool.fromEnvironment(
    'FLUTTER_APP_ENV',
    defaultValue: true,
  );
}
