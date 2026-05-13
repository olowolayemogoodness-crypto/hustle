import 'package:dio/dio.dart';
import 'package:hustle/core/network/dio_client.dart';

class SquadRepository {
  final Dio _dio = DioClient.instance;

  // ── Account Lookup ───────────────────────────────────────────────
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

  // ── Initiate Withdrawal ──────────────────────────────────────────
  Future<Map<String, dynamic>> initiateWithdrawal({
    required int    amountKobo,
    required String bankCode,
    required String accountNumber,
    required String accountName,
  }) async {
    final response = await _dio.post(
      '/wallet/withdraw',
      data: {
        'amount_kobo':     amountKobo,
        'bank_code':       bankCode,
        'account_number':  accountNumber,
        'account_name':    accountName,
      },
    );
    return response.data as Map<String, dynamic>;
  }

  // ── Get Wallet Balance ───────────────────────────────────────────
  Future<Map<String, dynamic>> getWalletBalance() async {
    final response = await _dio.get('/wallet/balance');
    return response.data as Map<String, dynamic>;
  }

  // ── Get Transaction History ──────────────────────────────────────
  Future<List<dynamic>> getTransactions({int limit = 20}) async {
    final response = await _dio.get(
      '/wallet/transactions',
      queryParameters: {'limit': limit},
    );
    return response.data['data'] as List<dynamic>;
  }

  // ── Release Escrow (Employer marks job complete) ─────────────────
  Future<void> releaseEscrow(String jobId) async {
    await _dio.post('/escrow/release', data: {'job_id': jobId});
  }

  // ── Get Virtual Account (for employer top-up) ────────────────────
  Future<Map<String, dynamic>> getVirtualAccount() async {
    final response = await _dio.get('/wallet/virtual-account');
    return response.data as Map<String, dynamic>;
  }
}