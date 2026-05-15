import 'package:flutter_dotenv/flutter_dotenv.dart';

class Env {
  Env._();

  static String get supabaseUrl      => _get('SUPABASE_URL');
  static String get supabaseAnonKey  => _get('SUPABASE_ANON_KEY');
  static String get mapTilerKey      => _get('MAPTILER_KEY');
  static String get termiiApiKey     => _get('TERMII_API_KEY');
  static String get termiiSenderId   => _get('TERMII_SENDER_ID');
  
  static String get squadPublicKey   => _get('SQUAD_PUBLIC_KEY');
// lib/core/env.dart
static String get apiBaseUrl => 
    dotenv.env['API_BASE_URL'] ?? 'http://localhost:8000';
  static String _get(String key) {
    final value = dotenv.env[key];
    assert(value != null && value.isNotEmpty, 
        '❌ Missing env variable: $key — check your .env file');
    return value!;
  }
}