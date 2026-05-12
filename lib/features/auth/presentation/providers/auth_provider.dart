import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:hustle/features/auth/data/models/auth_repository.dart';
import '../../data/models/auth_models.dart';

final authRepositoryProvider = Provider<AuthRepository>((ref) => AuthRepository());

// ── Session state ──────────────────────────────────────────────────
sealed class AuthState {
  const AuthState();
}
class AuthInitial      extends AuthState { const AuthInitial(); }
class AuthLoading      extends AuthState { const AuthLoading(); }
class AuthAuthenticated extends AuthState {
  const AuthAuthenticated(this.user);
  final AuthUser user;
}
class AuthUnauthenticated extends AuthState { const AuthUnauthenticated(); }
class AuthError        extends AuthState {
  const AuthError(this.message);
  final String message;
}

// ── Notifier ───────────────────────────────────────────────────────
class AuthNotifier extends Notifier<AuthState> {
  late final AuthRepository _repo;

  @override
  AuthState build() {
    _repo = ref.read(authRepositoryProvider);
    _checkStoredSession();
    return const AuthInitial();
  }

  Future<void> _checkStoredSession() async {
    final user = await _repo.getStoredUser();
    state = user != null
        ? AuthAuthenticated(user)
        : const AuthUnauthenticated();
  }

  Future<void> sendOtp(String phone) async {
    state = const AuthLoading();
    try {
      await _repo.sendOtp(phone);
      state = const AuthUnauthenticated(); // back to idle, OTP sent
    } on Exception catch (e) {
      state = AuthError(_parseError(e));
    }
  }

  Future<bool> verifyOtp(String phone, String otp) async {
    state = const AuthLoading();
    try {
      final session = await _repo.verifyOtp(phone, otp);
      state = AuthAuthenticated(session.user);
      return true;
    } on Exception catch (e) {
      state = AuthError(_parseError(e));
      return false;
    }
  }

  Future<void> setRole(String role) async {
    final current = state;
    if (current is! AuthAuthenticated) return;
    await _repo.setRole(role);
    state = AuthAuthenticated(current.user.copyWith(role: role));
  }

  Future<bool> submitKyc(String nin) async {
    final current = state;
    if (current is! AuthAuthenticated) return false;
    try {
      await _repo.submitKyc(nin);
      state = AuthAuthenticated(current.user.copyWith(kycStatus: 'verified'));
      return true;
    } on Exception catch (e) {
      state = AuthError(_parseError(e));
      return false;
    }
  }

  Future<void> signOut() async {
    await _repo.signOut();
    state = const AuthUnauthenticated();
  }

  String _parseError(Exception e) {
    final str = e.toString();
    if (str.contains('400')) return 'Invalid OTP or request.';
    if (str.contains('429')) return 'Too many attempts. Try again later.';
    if (str.contains('SocketException')) return 'No internet connection.';
    return 'Something went wrong. Please try again.';
  }
}

final authProvider =
    NotifierProvider<AuthNotifier, AuthState>(AuthNotifier.new);