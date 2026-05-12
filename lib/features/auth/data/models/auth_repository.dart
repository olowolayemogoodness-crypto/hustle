import 'package:dio/dio.dart';
import 'package:hustle/core/network/dio_client.dart';
import 'package:hustle/core/storage/secure_storage.dart';

import 'package:hustle/features/auth/data/models/auth_models.dart';

class AuthRepository {
  final Dio _dio = DioClient.instance;

  Future<void> sendOtp(String phone) async {
    await _dio.post('/auth/otp/send', data: {'phone': phone});
  }

  Future<AuthSession> verifyOtp(String phone, String otp) async {
    final response = await _dio.post(
      '/auth/otp/verify',
      data: {'phone': phone, 'otp': otp},
    );
    final session = AuthSession.fromJson(response.data as Map<String, dynamic>);

    // Persist session to secure storage immediately
    await SecureStorage.saveSession(
      token: session.token,
      userId: session.user.id,
      phone: session.user.phone,
      role: session.user.role,
      kycStatus: session.user.kycStatus,
    );

    return session;
  }

  Future<void> setRole(String role) async {
    await _dio.post('/auth/role', data: {'role': role});
    await SecureStorage.updateRole(role);
  }

  Future<Map<String, dynamic>> submitKyc(String nin) async {
    final response = await _dio.post('/auth/kyc/submit', data: {'nin': nin});
    await SecureStorage.updateKycStatus('verified');
    return response.data as Map<String, dynamic>;
  }

  Future<AuthUser?> getStoredUser() async {
    final hasSession = await SecureStorage.hasSession();
    if (!hasSession) return null;

    final id        = await SecureStorage.getUserId();
    final phone     = await SecureStorage.getPhone();
    final role      = await SecureStorage.getRole();
    final kycStatus = await SecureStorage.getKycStatus();

    if (id == null || phone == null) return null;

    return AuthUser(
      id: id,
      phone: phone,
      role: role,
      kycStatus: kycStatus ?? 'unverified',
    );
  }

  Future<void> signOut() => SecureStorage.clearSession();
}