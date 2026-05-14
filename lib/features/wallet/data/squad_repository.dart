import 'package:dio/dio.dart';
import 'package:hustle/core/network/dio_client.dart';

class SquadRepository {
  final Dio _dio = DioClient.instance;

  // ── Initiate Dynamic VA top-up ───────────────────────────────────
  Future<Map<String, dynamic>> initiateTopUp({
    required int amountKobo,
    required int duration,
  }) async {
    final response = await _dio.post(
      '/wallet/topup/initiate',
      data: {
        'amount_kobo': amountKobo,
        'duration':    duration,
      },
    );
    return response.data as Map<String, dynamic>;
  }

  // ── Poll payment status ──────────────────────────────────────────
  Future<Map<String, dynamic>> checkTopUpStatus(String reference) async {
    final response = await _dio.get('/wallet/topup/status/$reference');
    return response.data as Map<String, dynamic>;
  }

  // ── Wallet balance ───────────────────────────────────────────────
  Future<Map<String, dynamic>> getWalletBalance() async {
    final response = await _dio.get('/wallet/balance');
    return response.data as Map<String, dynamic>;
  }

  // ── Transaction history ──────────────────────────────────────────
  Future<List<dynamic>> getTransactions({int limit = 20}) async {
    final response = await _dio.get(
      '/wallet/transactions',
      queryParameters: {'limit': limit},
    );
    return response.data['data'] as List<dynamic>;
  }

  // ── Account lookup ───────────────────────────────────────────────
  Future<Map<String, dynamic>> lookupAccount({
    required String bankCode,
    required String accountNumber,
  }) async {
    final response = await _dio.post(
      '/wallet/lookup',
      data: {
        'bank_code':      bankCode,
        'account_number': accountNumber,
      },
    );
    return response.data as Map<String, dynamic>;
  }

  // ── Worker withdrawal ────────────────────────────────────────────
  Future<Map<String, dynamic>> initiateWithdrawal({
    required int    amountKobo,
    required String bankCode,
    required String accountNumber,
    required String accountName,
  }) async {
    final response = await _dio.post(
      '/wallet/withdraw',
      data: {
        'amount_kobo':    amountKobo,
        'bank_code':      bankCode,
        'account_number': accountNumber,
        'account_name':   accountName,
      },
    );
    return response.data as Map<String, dynamic>;
  }

  // ── Release escrow ───────────────────────────────────────────────
  Future<void> releaseEscrow(String jobId) async {
    await _dio.post('/escrow/release', data: {'job_id': jobId});
  }
}