import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hustle/core/network/dio_client.dart';
import '../../data/squad_repository.dart';
import '../../data/models/wallet_model.dart';

final squadRepositoryProvider = Provider((_) => SquadRepository());

// ── Wallet balance ───────────────────────────────────────────────────
// lib/features/wallet/presentation/providers/wallet_provider.dart
// lib/features/wallet/presentation/providers/wallet_provider.dart

class WalletNotifier extends AsyncNotifier<WalletState> {
  @override
  Future<WalletState> build() async {
    return _fetch();
  }
Future<WalletState> _fetch() async {
  try {
    final results = await Future.wait([
      DioClient.instance.get('/api/v1/wallet/balance'),
      DioClient.instance.get('/api/v1/wallet/transactions'),
    ]);

    print('Balance response: ${results[0].data}');      // ← add this
    print('Transactions response: ${results[1].data}'); // ← add this

    return WalletState.fromJson(
      balance:      results[0].data as Map<String, dynamic>,
      transactions: (results[1].data['data'] as List?) ?? [],
    );
  } catch (e) {
    print('Wallet fetch error: $e');  // ← add this
    return WalletState.mock();
  }
}

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(_fetch);
  }

  Future<bool> releaseEscrow(String jobId) async {
    try {
      await DioClient.instance.post(
        '/api/v1/escrow/release',
        data: {'job_id': jobId},
      );
      await refresh();
      return true;
    } catch (_) {
      return false;
    }
  }
}

final walletProvider =
    AsyncNotifierProvider<WalletNotifier, WalletState>(WalletNotifier.new);