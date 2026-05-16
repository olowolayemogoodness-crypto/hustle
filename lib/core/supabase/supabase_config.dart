import 'package:supabase_flutter/supabase_flutter.dart';
import '../env.dart';

class SupabaseConfig {
  SupabaseConfig._();

  static SupabaseClient get client => Supabase.instance.client;
  static GoTrueClient get auth => client.auth;

  static Future<void> init() async {
    await Supabase.initialize(
      url: Env.supabaseUrl,
      anonKey: Env.supabaseAnonKey,
      authOptions: const FlutterAuthClientOptions(
        authFlowType: AuthFlowType.pkce,
        autoRefreshToken: true,
      ),
    );

    // Refresh session on app startup
    final session = auth.currentSession;

    if (session != null) {
      try {
        final response = await auth.refreshSession();

        final newSession = response.session;

        if (newSession != null) {
          print('Session refreshed successfully');
          print('Expires at: ${newSession.expiresAt}');

          // Print full token safely
          printTokenInChunks(newSession.accessToken);
        }
      } catch (e) {
        print('Error refreshing session: $e');
      }
    }

    // Listen for auth state changes
    auth.onAuthStateChange.listen((data) {
      final event = data.event;
      final session = data.session;

      print('Auth event: $event');

      if (event == AuthChangeEvent.tokenRefreshed) {
        print('Token refreshed automatically');

        final token = session?.accessToken ?? '';

        printTokenInChunks(token);

        print('Expires at: ${session?.expiresAt}');
      }

      if (event == AuthChangeEvent.signedOut) {
        print('User signed out');
      }
    });
  }

  // Helper function to print long JWTs without truncation
  static void printTokenInChunks(String token) {
    const chunkSize = 200;

    for (int i = 0; i < token.length; i += chunkSize) {
      final end =
          (i + chunkSize < token.length)
              ? i + chunkSize
              : token.length;

      print('CHUNK: ${token.substring(i, end)}');
    }
  }
}