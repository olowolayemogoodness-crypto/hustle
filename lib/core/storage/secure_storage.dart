import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SecureStorage {
  SecureStorage._();

  static const _storage = FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );

  static const _kToken    = 'locgig_access_token';
  static const _kUserId   = 'locgig_user_id';
  static const _kPhone    = 'locgig_phone';
  static const _kRole     = 'locgig_role';
  static const _kKycStatus = 'locgig_kyc_status';

  static Future<void> saveSession({
    required String token,
    required String userId,
    required String phone,
    String? role,
    String? kycStatus,
  }) async {
    await Future.wait([
      _storage.write(key: _kToken, value: token),
      _storage.write(key: _kUserId, value: userId),
      _storage.write(key: _kPhone, value: phone),
      if (role != null) _storage.write(key: _kRole, value: role),
      if (kycStatus != null) _storage.write(key: _kKycStatus, value: kycStatus),
    ]);
  }

  static Future<String?> getToken()    => _storage.read(key: _kToken);
  static Future<String?> getUserId()   => _storage.read(key: _kUserId);
  static Future<String?> getPhone()    => _storage.read(key: _kPhone);
  static Future<String?> getRole()     => _storage.read(key: _kRole);
  static Future<String?> getKycStatus()=> _storage.read(key: _kKycStatus);

  static Future<bool> hasSession() async {
    final token = await getToken();
    return token != null && token.isNotEmpty;
  }

  static Future<void> updateRole(String role) =>
      _storage.write(key: _kRole, value: role);

  static Future<void> updateKycStatus(String status) =>
      _storage.write(key: _kKycStatus, value: status);

  static Future<void> clearSession() async {
    await Future.wait([
      _storage.delete(key: _kToken),
      _storage.delete(key: _kUserId),
      _storage.delete(key: _kPhone),
      _storage.delete(key: _kRole),
      _storage.delete(key: _kKycStatus),
    ]);
  }
}