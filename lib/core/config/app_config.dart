class AppConfig {
  AppConfig._();

  static const String apiBaseUrl =
      String.fromEnvironment('API_URL', defaultValue: 'https://api.locgig.app/api/v1');
  static const String mapsApiKey =
      String.fromEnvironment('MAPS_KEY', defaultValue: '');
  static const bool isDev =
      String.fromEnvironment('FLUTTER_APP_ENV', defaultValue: 'dev') == 'dev';
}