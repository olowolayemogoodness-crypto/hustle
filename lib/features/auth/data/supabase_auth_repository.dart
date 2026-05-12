import 'package:google_sign_in/google_sign_in.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../../../core/supabase/supabase_config.dart';

class SupabaseAuthRepository {
  SupabaseAuthRepository._();

  static final _auth   = SupabaseConfig.auth;
  static final _client = SupabaseConfig.client;

  static final _googleSignIn = GoogleSignIn(
    scopes: ['email', 'profile'],
  );

  // ── Current session ──────────────────────────────────────────────
  static Session? get currentSession => _auth.currentSession;
  static User?    get currentUser    => _auth.currentUser;

  static bool get isSignedIn => currentSession != null;

  /// Role stored in user_metadata after role selection
  static String? get userRole =>
      currentUser?.userMetadata?['role'] as String?;

  /// Stream — emits on every sign-in, sign-out, token refresh
  static Stream<AuthState> get authStateChanges =>
      _auth.onAuthStateChange;

  // ── Phone OTP ────────────────────────────────────────────────────

  /// Step 1 — send OTP to Nigerian phone number
  static Future<void> sendPhoneOtp(String phone) async {
    await _auth.signInWithOtp(
      phone: phone,
      // shouldCreateUser: true creates account on first OTP
      shouldCreateUser: true,
    );
  }

  /// Step 2 — verify the 6-digit code
  static Future<AuthResponse> verifyPhoneOtp({
    required String phone,
    required String otp,
  }) async {
    return _auth.verifyOTP(
      phone: phone,
      token: otp,
      type: OtpType.sms,
    );
  }

  // ── Google Sign-In ───────────────────────────────────────────────

  static Future<AuthResponse?> signInWithGoogle() async {
    final googleUser = await _googleSignIn.signIn();
    if (googleUser == null) return null; // user cancelled

    final googleAuth = await googleUser.authentication;

    if (googleAuth.idToken == null) {
      throw Exception('Google Sign-In failed: no ID token received.');
    }

    return _auth.signInWithIdToken(
      provider: OAuthProvider.google,
      idToken: googleAuth.idToken!,
      accessToken: googleAuth.accessToken,
    );
  }

  // ── Role ─────────────────────────────────────────────────────────

  /// Persists role in Supabase user_metadata + custom users table
  static Future<void> setRole(String role) async {
    // 1. Store in auth metadata (instant, no extra query needed)
    await _auth.updateUser(
      UserAttributes(data: {'role': role}),
    );

    // 2. Upsert into your custom users table
    await _client.from('users').upsert({
      'id':   currentUser!.id,
      'phone': currentUser!.phone,
      'email': currentUser!.email,
      'role':  role,
    });
  }

  // ── KYC ──────────────────────────────────────────────────────────

  static Future<void> submitKyc(String nin) async {
    await _client.from('kyc_submissions').insert({
      'user_id': currentUser!.id,
      'nin':     nin,
      'status':  'pending',
    });

    await _auth.updateUser(
      UserAttributes(data: {'kyc_status': 'pending'}),
    );
  }

  // ── Sign out ─────────────────────────────────────────────────────

  static Future<void> signOut() async {
    await _googleSignIn.signOut().catchError((_) {});
    await _auth.signOut();
  }

  // ── Profile refresh ──────────────────────────────────────────────

  static Future<Map<String, dynamic>?> fetchUserProfile() async {
    final userId = currentUser?.id;
    if (userId == null) return null;

    final result = await _client
        .from('users')
        .select()
        .eq('id', userId)
        .maybeSingle();

    return result;
  }
}