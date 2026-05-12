import 'package:supabase_flutter/supabase_flutter.dart';
import '../env.dart';

class SupabaseConfig {
  SupabaseConfig._();

  static SupabaseClient get client => Supabase.instance.client;
  static GoTrueClient   get auth   => client.auth;

  static Future<void> init() async {
    await Supabase.initialize(
      url:      Env.supabaseUrl,
      anonKey:  Env.supabaseAnonKey,
      authOptions: const FlutterAuthClientOptions(
        authFlowType: AuthFlowType.pkce,
        autoRefreshToken: true,
      ),
    );
  }
}