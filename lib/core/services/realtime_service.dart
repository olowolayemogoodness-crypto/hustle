// lib/core/services/realtime_service.dart
import 'package:supabase_flutter/supabase_flutter.dart';

class RealtimeService {
  RealtimeService._();

  static SupabaseClient get _client => Supabase.instance.client;

  /// Call once after login — connects realtime with user context
  static Future<void> init() async {
    final url    = const String.fromEnvironment('SUPABASE_URL');
    final anonKey = const String.fromEnvironment('SUPABASE_ANON_KEY');
    await Supabase.initialize(url: url, anonKey: anonKey);
  }

  /// Listen for application status changes (worker hired / rejected)
  static RealtimeChannel watchApplications({
    required String workerId,
    required void Function(Map<String, dynamic> payload) onUpdate,
  }) {
    return _client
        .channel('worker_applications_$workerId')
        .onPostgresChanges(
          event: PostgresChangeEvent.update,
          schema: 'public',
          table: 'applications',
          filter: PostgresChangeFilter(
            type: PostgresChangeFilterType.eq,
            column: 'worker_id',
            value: workerId,
          ),
          callback: (payload) => onUpdate(payload.newRecord),
        )
        .subscribe();
  }

  /// Listen for wallet credit events (payment released)
  static RealtimeChannel watchWallet({
    required String userId,
    required void Function(Map<String, dynamic> payload) onCredit,
  }) {
    return _client
        .channel('wallet_$userId')
        .onPostgresChanges(
          event: PostgresChangeEvent.insert,
          schema: 'public',
          table: 'wallet_transactions',
          filter: PostgresChangeFilter(
            type: PostgresChangeFilterType.eq,
            column: 'user_id',
            value: userId,
          ),
          callback: (payload) => onCredit(payload.newRecord),
        )
        .subscribe();
  }

  static Future<void> unsubscribeAll() async {
    await _client.removeAllChannels();
  }
}