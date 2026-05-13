import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/squad_repository.dart';
import '../../data/models/wallet_model.dart';

final squadRepositoryProvider = Provider((_) => SquadRepository());

// ── Wallet balance ───────────────────────────────────────────────────
class WalletNotifier extends AsyncNotifier<WalletState> {
  late final SquadRepository _repo;

  @override
  Future<WalletState> build() async {
    _repo = ref.read(squadRepositoryProvider);
    return _fetchWallet();
  }

  Future<WalletState> _fetchWallet() async {
    final results = await Future.wait([
      _repo.getWalletBalance(),
      _repo.getTransactions(),
    ]);
    return WalletState.fromJson(
      balance:      results[0] as Map<String, dynamic>,
      transactions: results[1] as List<dynamic>,
    );
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(_fetchWallet);
  }

  // ── Release escrow ─────────────────────────────────────────────────
  Future<bool> releaseEscrow(String jobId) async {
    try {
      await _repo.releaseEscrow(jobId);
      await refresh();
      return true;
    } catch (e) {
      return false;
    }
  }
}

final walletProvider =
    AsyncNotifierProvider<WalletNotifier, WalletState>(WalletNotifier.new);

// ── Withdrawal ──────────────────────────────────────────────────────────
class WithdrawalNotifier extends AsyncNotifier<void> {
  @override
  Future<void> build() async {}

  Future<String?> withdraw({
    required int    amountKobo,
    required String bankCode,
    required String accountNumber,
    required String accountName,
  }) async {
    state = const AsyncLoading();
    try {
      final repo   = ref.read(squadRepositoryProvider);
      final result = await repo.initiateWithdrawal(
        amountKobo:    amountKobo,
        bankCode:      bankCode,
        accountNumber: accountNumber,
        accountName:   accountName,
      );
      state = const AsyncData(null);
      // Refresh wallet balance
      ref.invalidate(walletProvider);
      return result['reference'] as String?;
    } catch (e) {
      state = AsyncError(e, StackTrace.current);
      return null;
    }
  }

  Future<Map<String, dynamic>?> lookupAccount({
    required String bankCode,
    required String accountNumber,
  }) async {
    try {
      final repo = ref.read(squadRepositoryProvider);
      return await repo.lookupAccount(
        bankCode:      bankCode,
        accountNumber: accountNumber,
      );
    } catch (_) {
      return null;
    }
  }
}

final withdrawalProvider =
    AsyncNotifierProvider<WithdrawalNotifier, void>(WithdrawalNotifier.new);