import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hustle/features/auth/presentation/providers/auth_provider.dart';
import 'package:hustle/features/auth/data/models/auth_models.dart';
// Convenience read-only provider — use this in UI widgets
final currentUserProvider = Provider<AuthUser?>((ref) {
  final authState = ref.watch(authProvider);
  return authState is AuthAuthenticated ? authState.user : null;
});