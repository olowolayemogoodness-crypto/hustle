import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hustle/features/auth/data/models/auth_repository.dart';
import 'package:supabase_flutter/supabase_flutter.dart'
    hide AuthUser;
import 'package:hustle/features/auth/data/models/auth_models.dart';
import 'dart:async';


sealed class AppAuthState { const AppAuthState(); }
class AuthInitial         extends AppAuthState { const AuthInitial(); }
class AuthLoading         extends AppAuthState { const AuthLoading(); }
class AuthAuthenticated   extends AppAuthState {
  const AuthAuthenticated(this.user);
  final AuthUser user;
}
class AuthUnauthenticated extends AppAuthState { const AuthUnauthenticated(); }
class AuthError           extends AppAuthState {
  const AuthError(this.message);
  final String message;
}

class AuthNotifier extends Notifier<AppAuthState> {
  late StreamSubscription _subscription;

  @override
  AppAuthState build() {
    // Start listening to auth changes immediately
    _subscribeToSupabase();
    
    // Register cleanup
    ref.onDispose(() {
      _subscription.cancel();
    });
    
    // Check for existing session synchronously
    final session = AuthRepository.currentSession;
    if (session != null) {
      return AuthAuthenticated(AuthUser.fromSupabase(session.user));
    }
    
    // If no session yet, stay in AuthLoading to allow stream to resolve
    // The stream will emit initialSession event and update state
    return const AuthLoading();
  }

  void checkSession() {
    final session = AuthRepository.currentSession;
    if (session == null) {
      state = const AuthUnauthenticated();
    } else {
      state = AuthAuthenticated(AuthUser.fromSupabase(session.user));
    }
  }

  void _subscribeToSupabase() {
    _subscription = AuthRepository.authStateChanges.listen((supabaseState) {
      switch (supabaseState.event) {
        case AuthChangeEvent.signedIn:
        case AuthChangeEvent.tokenRefreshed:
        case AuthChangeEvent.userUpdated:
        case AuthChangeEvent.initialSession:
          final user = supabaseState.session?.user;
          if (user != null) {
            state = AuthAuthenticated(AuthUser.fromSupabase(user));
          } else if (supabaseState.event == AuthChangeEvent.initialSession) {
            // initialSession with no user means user is not logged in
            state = const AuthUnauthenticated();
          }
        case AuthChangeEvent.signedOut:
          state = const AuthUnauthenticated();
        default:
          break;
      }
    });
  }

  // ── Google Sign-In ───────────────────────────────────────────────
  Future<bool> signInWithGoogle() async {
    state = const AuthLoading();
    try {
      final response = await AuthRepository.signInWithGoogle();
      if (response == null) {
        state = const AuthUnauthenticated();
        return false;
      }
      if (response.user != null) {
        state = AuthAuthenticated(AuthUser.fromSupabase(response.user!));
        return true;
      }
      state = const AuthError('Google sign-in failed.');
      return false;
    } catch (e) {
      state = AuthError(_parseError(e));
      return false;
    }
  }

  // ── Role ─────────────────────────────────────────────────────────
  Future<void> setRole(String role) async {
    final current = state;
    if (current is! AuthAuthenticated) return;
    try {
      await AuthRepository.setRole(role);
      state = AuthAuthenticated(current.user.copyWith(role: role));
    } catch (e) {
      state = AuthError(_parseError(e));
    }
  }

  // ── KYC ──────────────────────────────────────────────────────────
  Future<bool> submitKyc(String nin) async {
    final current = state;
    if (current is! AuthAuthenticated) return false;
    try {
      await AuthRepository.submitKyc(nin);
      state = AuthAuthenticated(current.user.copyWith(kycStatus: 'pending'));
      return true;
    } catch (e) {
      state = AuthError(_parseError(e));
      return false;
    }
  }

  // ── Sign out ─────────────────────────────────────────────────────
  Future<void> signOut() async {
    await AuthRepository.signOut();
    state = const AuthUnauthenticated();
  }

  String _parseError(Object e) {
    final msg = e.toString().toLowerCase();
    if (msg.contains('network') || msg.contains('socket')) return 'No internet connection.';
    if (msg.contains('cancelled') || msg.contains('canceled')) return 'Sign-in cancelled.';
    return e.toString();
  }
}

final authProvider =
    NotifierProvider<AuthNotifier, AppAuthState>(AuthNotifier.new);

final currentUserProvider = Provider<AuthUser?>((ref) {
  final s = ref.watch(authProvider);
  return s is AuthAuthenticated ? s.user : null;
});

final isAuthenticatedProvider = Provider<bool>((ref) {
  return ref.watch(authProvider) is AuthAuthenticated;
});