import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:hustle/features/auth/presentation/screens/phone_auth_screen.dart';
import 'package:hustle/features/auth/presentation/screens/role_select_screen.dart';
import 'package:hustle/features/discovery/presentation/screens/map_view_screen.dart';
import 'package:hustle/features/jobs/presentation/screens/jobs_details.dart';
import 'package:hustle/features/onboarding/presentation/screens/splash_screen.dart';
import 'package:hustle/features/onboarding/presentation/screens/worker_setup_screen.dart';
import 'package:hustle/features/profile/presentation/screens/worker_profile_screen.dart';
import 'package:hustle/features/wallet/presentation/screens/wallet_screen.dart';
import 'package:hustle/shared/widgets/bottom_nav.dart';
import '../../features/auth/presentation/providers/auth_provider.dart';
import 'routes.dart';

const _navRoutes = [
  Routes.discovery,
  Routes.mapView,
  Routes.wallet,
  Routes.profile,
];

int _navIndex(String location) {
  final i = _navRoutes.indexWhere((r) => location.startsWith(r));
  return i < 0 ? 0 : i;
}

final appRouterProvider = Provider<GoRouter>((ref) {
  final notifier = ValueNotifier<AppAuthState>(const AuthInitial());

  ref.listen<AppAuthState>(authProvider, (_, next) {
    notifier.value = next;
  });

  return GoRouter(
    initialLocation: Routes.splash,
    refreshListenable: notifier,
    redirect: (context, state) {
      final auth     = notifier.value;
      final location = state.matchedLocation;

      // Still initialising → stay on splash
      if (auth is AuthInitial || auth is AuthLoading) {
        return Routes.splash;
      }

      // Not logged in → login
      if (auth is AuthUnauthenticated) {
        if (location == Routes.phoneAuth ||
            location == Routes.splash) return null;
        return Routes.phoneAuth;
      }

      // Logged in
      if (auth is AuthAuthenticated) {
        final user = auth.user;

        // Coming from splash/login → route to right place
        if (location == Routes.splash ||
            location == Routes.phoneAuth) {
          if (user.needsRole) return Routes.roleSelect;
          return Routes.discovery;
        }

        // Has role step pending
        if (user.needsRole &&
            location != Routes.roleSelect &&
            location != Routes.workerSetup) {
          return Routes.roleSelect;
        }
      }

      return null;
    },
    routes: [
      // ── Fullscreen — no bottom nav ──────────────────────────────
      GoRoute(
        path: Routes.splash,
        builder: (_, __) => const SplashScreen(),
      ),
      GoRoute(
        path: Routes.phoneAuth,
        builder: (_, __) => const PhoneAuthScreen(),
      ),
      GoRoute(
        path: Routes.roleSelect,
        builder: (_, __) => const RoleSelectScreen(),
      ),
      GoRoute(
        path: Routes.workerSetup,
        builder: (_, __) => const WorkerSetupScreen(),
      ),

      // ── Shell — bottom nav visible on all 4 tabs ────────────────
      ShellRoute(
        builder: (context, state, child) => Scaffold(
          body: child,
          bottomNavigationBar: LGBottomNav(
            currentIndex: _navIndex(state.matchedLocation),
            onTap: (i) => context.go(_navRoutes[i]),
          ),
        ),
        routes: [
          GoRoute(
            path: Routes.discovery,
            builder: (_, __) => const DiscoveryScreen(),
          ),
          GoRoute(
            path: Routes.mapView,
            builder: (_, __) => const MapViewScreen(),
          ),
          GoRoute(
            path: Routes.wallet,
            builder: (_, __) => const WalletScreen(),
          ),
          GoRoute(
            path: Routes.profile,
            builder: (_, __) => const WorkerProfileScreen(),
          ),
        ],
      ),
    ],
  );
});