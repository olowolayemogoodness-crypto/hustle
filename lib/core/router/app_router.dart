import 'dart:ui';

import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:hustle/features/discovery/presentation/screens/map_view_screen.dart';
import 'package:hustle/features/jobs/presentation/screens/jobs_details.dart';
import 'package:hustle/features/profile/presentation/screens/job_details.dart';
import 'package:hustle/shared/widgets/bottom_nav.dart';
import '../../features/wallet/presentation/screens/wallet_screen.dart';
import '../../features/profile/presentation/screens/worker_profile_screen.dart';
import 'routes.dart';


final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: Routes.profile,
    routes: [
      
      // lib/core/router/app_router.dart — add mapView route
GoRoute(
  path: Routes.mapView,
  builder: (context, state) => const MapViewScreen(),
),

GoRoute(
        path: Routes.discovery,
        builder: (context, state) => const DiscoveryScreen(),
      ),
      GoRoute(
        path: Routes.wallet,
        builder: (context, state) => const WalletScreen(),
      ),
     
      
      GoRoute(
        path: Routes.jobDetail,
        builder: (context, state) => const JobDetails(),
      ),
    ],
  );
});