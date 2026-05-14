import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:hustle/features/auth/presentation/screens/phone_auth_screen.dart';
import 'package:hustle/features/auth/presentation/screens/role_select_screen.dart';
import 'package:hustle/features/discovery/presentation/screens/map_view_screen.dart';
import 'package:hustle/features/jobs/presentation/screens/jobs_details.dart';
import 'package:hustle/features/auth/presentation/screens/onboarding_screen.dart';
import 'package:hustle/features/onboarding/presentation/screens/splash_screen.dart';
import 'package:hustle/features/onboarding/presentation/screens/worker_setup_screen.dart';
import 'package:hustle/features/profile/presentation/screens/worker_profile_screen.dart';
import 'package:hustle/features/wallet/presentation/screens/wallet_screen.dart';
import 'package:hustle/shared/widgets/bottom_nav.dart';
import 'package:hustle/core/storage/secure_storage.dart';
import '../../features/auth/presentation/providers/auth_provider.dart';
import 'routes.dart';

const _navRoutes = [
  Routes.discovery, // index 0 — Jobs
  Routes.mapView,   // index 1 — Discover
  Routes.wallet,    // index 2 — Wallet
  Routes.profile,   // index 3 — Profile
];

int _navIndex(String location) {
  if (location == Routes.mapView)   return 1;
  if (location == Routes.wallet)    return 2;
  if (location == Routes.profile)   return 3;
  return 0; // discovery is default
}

final appRouterProvider = Provider<GoRouter>((ref) {
  final notifier = ValueNotifier<AppAuthState>(const AuthInitial());
  final seenOnboardingNotifier = ValueNotifier<bool?>(null);

  // Load onboarding flag on startup
  WidgetsBinding.instance.addPostFrameCallback((_) async {
    final seen = await SecureStorage.hasSeenOnboarding();
    seenOnboardingNotifier.value = seen;
  });

  ref.listen<AppAuthState>(authProvider, (_, next) {
    notifier.value = next;
  });

  return GoRouter(
    initialLocation: Routes.splash,
    refreshListenable: Listenable.merge([notifier, seenOnboardingNotifier]),
    redirect: (context, state) {
      final auth     = notifier.value;
      final location = state.matchedLocation;
      final seenOnboarding = seenOnboardingNotifier.value;

      if (auth is AuthInitial || auth is AuthLoading) return Routes.splash;

      if (auth is AuthUnauthenticated) {
        if (location == Routes.phoneAuth ||
            location == Routes.onboarding ||
            location == Routes.splash) {
          if (location == Routes.splash) {
            // If onboarding flag not yet loaded, stay on splash
            if (seenOnboarding == null) return Routes.splash;
            // Otherwise, show onboarding only if not seen
            return seenOnboarding ? Routes.phoneAuth : Routes.onboarding;
          }
          return null;
        }
        return Routes.phoneAuth;
      }

      if (auth is AuthAuthenticated) {
        final user = auth.user;

        if (location == Routes.splash ||
            location == Routes.phoneAuth ||
            location == Routes.onboarding) {
          if (user.needsRole) return Routes.roleSelect;
          return Routes.discovery;
        }

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
      GoRoute(path: Routes.splash,      builder: (_, __) => const SplashScreen()),
      GoRoute(path: Routes.onboarding,  builder: (_, __) => const OnboardingScreen()),
      GoRoute(path: Routes.phoneAuth,   builder: (_, __) => const PhoneAuthScreen()),
      GoRoute(path: Routes.roleSelect,  builder: (_, __) => const RoleSelectScreen()),
      GoRoute(path: Routes.workerSetup, builder: (_, __) => const WorkerSetupScreen()),

      // ── Shell — bottom nav visible ──────────────────────────────
      ShellRoute(
        builder: (context, state, child) => Scaffold(
          body: child,
          bottomNavigationBar: LGBottomNav(
            currentIndex: _navIndex(state.matchedLocation),
            onTap: (i) => context.go(_navRoutes[i]),
          ),
        ),
        routes: [
          GoRoute(path: Routes.discovery, builder: (_, __) => const DiscoveryScreen()),
          GoRoute(path: Routes.mapView,   builder: (_, __) => const MapViewScreen()),
          GoRoute(path: Routes.wallet,    builder: (_, __) => const WalletScreen()),
          GoRoute(path: Routes.profile,   builder: (_, __) => const WorkerProfileScreen()),
        ],
      ),
    ],
  );
});