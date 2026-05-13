class Routes {
  Routes._();
  static const String splash       = '/';
  static const String phoneAuth    = '/auth/phone';

  static const String roleSelect   = '/auth/role';
  static const String workerSetup  = '/auth/setup';   // ← add this
  static const String kyc          = '/auth/kyc';
  static const String discovery    = '/discovery';
  static const String wallet       = '/wallet';
  static const String profile      = '/profile';
  static const String jobDetail    = '/job/:id';
  static const String mapView = '/map'; // ← no longer /discovery/map
}


