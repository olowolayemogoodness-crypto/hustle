// lib/core/router/routes.dart
class Routes {
  Routes._();
  static const String splash      = '/';
  static const String discovery   = '/discovery';
  static const String mapView     = '/discovery/map';   // ← new
  static const String wallet      = '/wallet';
  static const String profile     = '/profile';
  static const String jobDetail   = '/job/:id';
}