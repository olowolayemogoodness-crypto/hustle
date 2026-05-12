import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter/material.dart';
import 'package:hustle/features/auth/presentation/screens/worker_setup_screen.dart';
import 'package:hustle/features/jobs/presentation/screens/jobs_details.dart';
import '../../features/auth/presentation/providers/auth_provider.dart';
import '../../features/auth/data/models/auth_models.dart';
import '../../features/auth/presentation/screens/phone_auth_screen.dart';

import '../../features/auth/presentation/screens/role_select_screen.dart';


import 'package:hustle/features/auth/presentation/screens/otp_screen.dart';
import 'package:hustle/features/discovery/presentation/screens/map_view_screen.dart';
import '../../features/discovery/presentation/screens/map_view_screen.dart';
import '../../features/wallet/presentation/screens/wallet_screen.dart';
import '../../features/profile/presentation/screens/worker_profile_screen.dart';
import 'routes.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  final authListenable = ValueNotifier<AuthState>(const AuthInitial());

  ref.listen<AuthState>(authProvider, (_, next) {
    authListenable.value = next;
  });

  return GoRouter(
    initialLocation: Routes.phoneAuth,
    refreshListenable: authListenable,
    redirect: (context, routerState) {
      final authState = authListenable.value;
      final location  = routerState.matchedLocation;

      // Still initialising
      if (authState is AuthInitial || authState is AuthLoading) {
        return Routes.splash;
      }

      // Not logged in → phone auth
      if (authState is AuthUnauthenticated) {
        if (location == Routes.phoneAuth ||
            location == Routes.otp       ||
            location == Routes.splash) return null;
        return Routes.phoneAuth;
      }

      // Logged in
      if (authState is AuthAuthenticated) {
        final user = authState.user;

        // On splash/auth screens → push to right destination
        if (location == Routes.splash    ||
            location == Routes.phoneAuth ||
            location == Routes.otp) {
          if (user.needsRole)  return Routes.roleSelect;
          if (!user.isVerified) return Routes.discovery; // KYC optional
          return Routes.discovery;
        }

        // Needs role but trying to go elsewhere
        if (user.needsRole && location != Routes.roleSelect) {
          return Routes.roleSelect;
        }
      }

      return null; // no redirect
    },
    routes: [
    
    GoRoute(
  path: Routes.workerSetup,
  builder: (_, __) => const WorkerSetupScreen(),
),

    
      GoRoute(
        path: Routes.otp,
        builder: (context, state) {
          final phone = state.extra as String;
          return OtpScreen(phone: phone);
        },
      ),
      GoRoute(path: Routes.roleSelect,
          builder: (_, __) => const RoleSelectScreen()),
      GoRoute(path: Routes.phoneAuth,
          builder: (_, __) => const PhoneAuthScreen()),
      GoRoute(path: Routes.discovery,
          builder: (_, __) => const DiscoveryScreen()),
      GoRoute(path: Routes.mapView,
          builder: (_, __) => const MapViewScreen()),
      GoRoute(path: Routes.wallet,
          builder: (_, __) => const WalletScreen()),
      GoRoute(path: Routes.profile,
          builder: (_, __) => const WorkerProfileScreen()),
    ],
  );
});