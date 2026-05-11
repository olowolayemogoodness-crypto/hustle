import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hustle/features/discovery/presentation/screens/discovery_page.dart';
import 'package:hustle/features/profile/presentation/screens/job_details.dart';
import 'package:hustle/features/profile/presentation/screens/worker_profile_screen.dart';
import 'package:hustle/features/wallet/presentation/screens/wallet_screen.dart';

import 'shared/widgets/bottom_nav.dart';

final bottomNavIndexProvider = StateProvider<int>((ref) => 0);

class HustleApp extends ConsumerWidget {
  const HustleApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentIndex = ref.watch(bottomNavIndexProvider);

    final screens = [
      const DiscoveryPage(),
      const JobDetails(),
      const WalletScreen(),
      const WorkerProfileScreen(),
    ];

    void onTap(int index) {
      ref.read(bottomNavIndexProvider.notifier).state = index;
    }

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: Scaffold(
        body: screens[currentIndex],
        bottomNavigationBar: LGBottomNav(
          currentIndex: currentIndex,
          onTap: onTap,
        ),
      ),
    );
  }
}