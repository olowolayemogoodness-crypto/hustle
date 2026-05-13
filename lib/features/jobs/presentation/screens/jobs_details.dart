import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:hustle/features/profile/presentation/screens/worker_profile_screen.dart';
import '../../../../core/config/theme.dart';
import '../../../../core/utils/formatters.dart';
import '../../../../core/router/routes.dart';
import '../../data/models/job_model.dart';
import '../providers/filter_provider.dart';
import '../providers/jobs_provider.dart';

class DiscoveryScreen extends ConsumerWidget {
  const DiscoveryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      backgroundColor: AppColors.backgroundWhite,
      body: SafeArea(
        child: Column(
          children: [
            _DiscoveryHeader(),
            Expanded(
              child: SingleChildScrollView(
                child: Column(
                  children: [
                    const SizedBox(height: 16),
                    const _TrustScoreBanner(),
                    const SizedBox(height: 16),
                    const Padding(
                      padding: EdgeInsets.symmetric(horizontal: 16),
                      child: _SearchAndToggleRow(),
                    ),
                    const SizedBox(height: 12),
                    const Padding(
                      padding: EdgeInsets.symmetric(horizontal: 16),
                      child: _FilterTabs(),
                    ),
                    const SizedBox(height: 14),
                    const _JobsList(),
                    const SizedBox(height: 24),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
      
    );
  }
}

// ─────────────────────────── Header ────────────────────────────

class _DiscoveryHeader extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final greeting = _getGreeting();

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                RichText(
                  text: TextSpan(
                    children: [
                      TextSpan(
                        text: '$greeting, Emeka ',
                        style: const TextStyle(
                          fontFamily: 'Syne',
                          fontSize: 19,
                          fontWeight: FontWeight.w200,
                          color: AppColors.textPrimary,
                        ),
                      ),
                      const TextSpan(
                        text: '👋',
                        style: TextStyle(fontSize: 22),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    Container(
                      width: 8,
                      height: 8,
                      decoration: const BoxDecoration(
                        color: AppColors.success,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 6),
                    const Text(
                      'Lagos, Mainland',
                      style: TextStyle(
                        fontFamily: 'DMSans',
                        fontSize: 13,
                        fontWeight: FontWeight.w500,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          
           
            _AvatarWithBadge(),
        ],
      ),
    );
  }

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  }
}

class _AvatarWithBadge extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: ()=> Navigator.push(
              context,
              MaterialPageRoute(builder: (context) =>  WorkerProfileScreen()),
            ),
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          CircleAvatar(
            radius: 24,
            backgroundColor: AppColors.borderLight,
            child: const Text(
              'E',
              style: TextStyle(
                fontFamily: 'Syne',
                fontWeight: FontWeight.w700,
                fontSize: 18,
                color: AppColors.primaryGreen,
              ),
            ),
          ),
          Positioned(
            right: 0,
            bottom: 0,
            child: Container(
              width: 16,
              height: 16,
              decoration: const BoxDecoration(
                color: AppColors.primaryGreen,
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.check, color: Colors.white, size: 10),
            ),
          ),
        ],
      ),
    );
  }
}

// In job posting screen — show employer what they'll pay
class _FeeBreakdown extends StatelessWidget {
  const _FeeBreakdown({required this.jobValueKobo});
  final int jobValueKobo;

  int get platformFee  => (jobValueKobo * 2 / 100).round();
  int get totalCharge  => jobValueKobo + platformFee;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.primaryGreenLight,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.primaryGreen.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          _Row('Job value',    Formatters.naira(jobValueKobo),
              color: AppColors.textPrimary),
          const SizedBox(height: 8),
          _Row('Platform fee (2%)', Formatters.naira(platformFee),
              color: AppColors.textSecondary),
          const Divider(height: 20),
          _Row('You pay',     Formatters.naira(totalCharge),
              color: AppColors.primaryGreen, bold: true),
          const SizedBox(height: 4),
          _Row('Worker gets', Formatters.naira(jobValueKobo),
              color: AppColors.primaryGreen, bold: true),
        ],
      ),
    );
  }
}

class _Row extends StatelessWidget {
  const _Row(this.label, this.value, {
    required this.color,
    this.bold = false,
  });

  final String label, value;
  final Color  color;
  final bool   bold;

  @override
  Widget build(BuildContext context) {
    final style = TextStyle(
      fontFamily: 'DMSans',
      fontSize:   bold ? 15 : 13.5,
      fontWeight: bold ? FontWeight.w700 : FontWeight.w400,
      color:      color,
    );
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: style),
        Text(value,  style: style),
      ],
    );
  }
}

// ─────────────────────────── Trust Score Banner ────────────────────────────

class _TrustScoreBanner extends StatelessWidget {
  const _TrustScoreBanner();

  @override
  Widget build(BuildContext context) {
    const score = 4.8;
    const progressValue = score / 5.0;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.fromLTRB(18, 16, 18, 16),
        decoration: BoxDecoration(
          color: AppColors.primaryGreen,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Text(
                        'Trust Score  ',
                        style: TextStyle(
                          fontFamily: 'DMSans',
                          fontSize: 15,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                        ),
                      ),
                      const Icon(Icons.star_rounded,
                          color: Color(0xFFFFB800), size: 17),
                      const SizedBox(width: 3),
                      const Text(
                        '4.8',
                        style: TextStyle(
                          fontFamily: 'Syne',
                          fontSize: 17,
                          fontWeight: FontWeight.w800,
                          color: Colors.white,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'Top 10% in your area',
                    style: TextStyle(
                      fontFamily: 'DMSans',
                      fontSize: 12,
                      color: Colors.white70,
                    ),
                  ),
                  const SizedBox(height: 10),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: progressValue,
                      backgroundColor: Colors.white.withOpacity(0.25),
                      valueColor: const AlwaysStoppedAnimation<Color>(
                          Color(0xFF4ADE80)),
                      minHeight: 6,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 16),
            Container(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.15),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.shield_outlined,
                  color: Colors.white, size: 22),
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────── Search & Toggle Row ────────────────────────────

class _SearchAndToggleRow extends ConsumerWidget {
  const _SearchAndToggleRow();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isListView = ref.watch(viewToggleProvider);

    return Row(
      children: [
        Expanded(
          child: Container(
            height: 46,
            decoration: BoxDecoration(
              color: AppColors.backgroundGrey,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                const SizedBox(width: 12),
                const Icon(Icons.search_rounded,
                    color: AppColors.textSecondary, size: 20),
                const SizedBox(width: 8),
                Expanded(
                  child: TextField(
                    decoration: const InputDecoration(
                      hintText: 'Search nearby jobs...',
                      hintStyle: TextStyle(
                        fontFamily: 'DMSans',
                        fontSize: 13.5,
                        color: AppColors.textHint,
                      ),
                      border: InputBorder.none,
                      isDense: true,
                      contentPadding: EdgeInsets.zero,
                    ),
                    style: const TextStyle(
                      fontFamily: 'DMSans',
                      fontSize: 13.5,
                      color: AppColors.textPrimary,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(width: 8),
        // Filter icon
        _ToggleIconBtn(
          icon: Icons.tune_rounded,
          isActive: false,
          onTap: () {},
        ),
        const SizedBox(width: 6),
        // Map view icon
        _ToggleIconBtn(
          icon: Icons.map_outlined,
          isActive: !isListView,
          onTap: () {
            ref.read(viewToggleProvider.notifier).toggleToMap();
            context.go(Routes.mapView);
          },
        ),
        const SizedBox(width: 6),
        // List view icon
        _ToggleIconBtn(
          icon: Icons.list_rounded,
          isActive: isListView,
          onTap: () {
            ref.read(viewToggleProvider.notifier).toggleToList();
          },
        ),
      ],
    );
  }
}

class _ToggleIconBtn extends StatelessWidget {
  const _ToggleIconBtn({
    required this.icon,
    required this.isActive,
    required this.onTap,
  });

  final IconData icon;
  final bool isActive;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 42,
        height: 46,
        decoration: BoxDecoration(
          color: isActive ? AppColors.primaryGreen : AppColors.backgroundGrey,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Icon(
          icon,
          color: isActive ? Colors.white : AppColors.textSecondary,
          size: 20,
        ),
      ),
    );
  }
}

// ─────────────────────────── Filter Tabs ────────────────────────────

class _FilterTabs extends ConsumerWidget {
  const _FilterTabs();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selected = ref.watch(filterProvider);

    final filters = [
      (JobFilter.nearby, 'Nearby'),
      (JobFilter.topPaying, 'Top Paying'),
      (JobFilter.urgent, 'Urgent'),
    ];

    return Row(
      children: filters.map((entry) {
        final (filter, label) = entry;
        final isActive = selected == filter;

        return Padding(
          padding: const EdgeInsets.only(right: 8),
          child: GestureDetector(
            onTap: () {
              ref.read(filterProvider.notifier).select(filter);
              ref.read(jobsProvider.notifier).applyFilter(filter);
            },
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              padding:
                  const EdgeInsets.symmetric(horizontal: 16, vertical: 9),
              decoration: BoxDecoration(
                color: isActive
                    ? AppColors.primaryGreen
                    : Colors.transparent,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: isActive
                      ? AppColors.primaryGreen
                      : AppColors.borderLight,
                  width: 1.5,
                ),
              ),
              child: Text(
                label,
                style: TextStyle(
                  fontFamily: 'DMSans',
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: isActive ? Colors.white : AppColors.textSecondary,
                ),
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
}

// ─────────────────────────── Jobs List ────────────────────────────

class _JobsList extends ConsumerWidget {
  const _JobsList();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final jobsAsync = ref.watch(jobsProvider);

    return jobsAsync.when(
      loading: () => const Padding(
        padding: EdgeInsets.symmetric(vertical: 40),
        child: Center(
          child: CircularProgressIndicator(color: AppColors.primaryGreen),
        ),
      ),
      error: (e, _) => Padding(
        padding: const EdgeInsets.all(24),
        child: Text('Error: $e'),
      ),
      data: (jobs) => Column(
        children: jobs
            .map((job) => Padding(
                  padding: const EdgeInsets.fromLTRB(16, 0, 16, 10),
                  child: _JobCard(job: job),
                ))
            .toList(),
      ),
    );
  }
}

// ─────────────────────────── Job Card ────────────────────────────

class _JobCard extends StatelessWidget {
  const _JobCard({required this.job});
  final JobListing job;

  @override
  Widget build(BuildContext context) {
    final accent = job.accentColor.color;

    return GestureDetector(
      onTap: () => context.go('${Routes.jobDetail.replaceFirst(':id', job.id)}'),
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppColors.borderLight),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.04),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(16),
          child: IntrinsicHeight(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Left accent bar
                Container(width: 4, color: accent),
                // Card body
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.all(14),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Top row: icon + title + pay
                        Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            _JobIcon(
                              emoji: job.iconEmoji,
                              color: job.iconColor,
                              isAvatar: job.employerAvatarUrl != null,
                              avatarUrl: job.employerAvatarUrl,
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    job.title,
                                    style: const TextStyle(
                                      fontFamily: 'DMSans',
                                      fontSize: 14.5,
                                      fontWeight: FontWeight.w700,
                                      color: AppColors.textPrimary,
                                    ),
                                  ),
                                  const SizedBox(height: 3),
                                  Row(
                                    children: [
                                      const Icon(
                                        Icons.location_on_outlined,
                                        size: 12,
                                        color: AppColors.textSecondary,
                                      ),
                                      const SizedBox(width: 2),
                                      Text(
                                        job.locationName,
                                        style: const TextStyle(
                                          fontFamily: 'DMSans',
                                          fontSize: 12,
                                          color: AppColors.textSecondary,
                                        ),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text(
                              Formatters.naira(job.payKobo),
                              style: TextStyle(
                                fontFamily: 'Syne',
                                fontSize: 15,
                                fontWeight: FontWeight.w800,
                                color: accent,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 10),
                        // Tags row
                        Row(
                          children: [
                            Expanded(
                              child: Wrap(
                                spacing: 6,
                                runSpacing: 6,
                                children: [
                                  _buildUrgencyTag(job),
                                  if (job.hasEscrow) _buildEscrowTag(),
                                  _buildDistanceTag(job),
                                ],
                              ),
                            ),
                            const SizedBox(width: 8),
                            _StarRow(rating: job.rating),
                          ],
                        ),
                        const SizedBox(height: 12),
                        // Apply button
                        _ApplyButton(
                          job: job,
                          accentColor: accent,
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildUrgencyTag(JobListing job) {
    Color tagColor;
    switch (job.urgencyType) {
      case JobUrgencyType.todayOnly:
        tagColor = const Color(0xFFF59E0B);
        break;
      case JobUrgencyType.daysLeft:
        tagColor = const Color(0xFF6B7280);
        break;
      case JobUrgencyType.open:
        tagColor = AppColors.primaryGreen;
        break;
    }

    return _TagPill(
      label: job.urgencyLabel,
      color: tagColor,
      icon: job.urgencyType == JobUrgencyType.todayOnly
          ? Icons.access_time_rounded
          : null,
    );
  }

  Widget _buildEscrowTag() => _TagPill(
        label: 'Escrow',
        color: AppColors.primaryGreen,
        icon: Icons.shield_outlined,
      );

  Widget _buildDistanceTag(JobListing job) => _TagPill(
        label: job.distanceDisplay,
        color: AppColors.textSecondary,
        isFilled: false,
      );
}

class _JobIcon extends StatelessWidget {
  const _JobIcon({
    required this.emoji,
    required this.color,
    required this.isAvatar,
    this.avatarUrl,
  });

  final String emoji;
  final Color color;
  final bool isAvatar;
  final String? avatarUrl;

  @override
  Widget build(BuildContext context) {
    if (isAvatar && avatarUrl != null) {
      return CircleAvatar(
        radius: 22,
        backgroundImage: NetworkImage(avatarUrl!),
      );
    }

    return Container(
      width: 44,
      height: 44,
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        shape: BoxShape.circle,
      ),
      child: Center(
        child: Text(emoji, style: const TextStyle(fontSize: 20)),
      ),
    );
  }
}

class _TagPill extends StatelessWidget {
  const _TagPill({
    required this.label,
    required this.color,
    this.icon,
    this.isFilled = false,
  });

  final String label;
  final Color color;
  final IconData? icon;
  final bool isFilled;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: isFilled ? color.withOpacity(0.1) : Colors.transparent,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.5), width: 1.2),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 11, color: color),
            const SizedBox(width: 3),
          ],
          Text(
            label,
            style: TextStyle(
              fontFamily: 'DMSans',
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}

class _StarRow extends StatelessWidget {
  const _StarRow({required this.rating});
  final double rating;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: List.generate(5, (i) {
        if (i < rating.floor()) {
          return const Icon(Icons.star_rounded,
              size: 13, color: AppColors.starColor);
        } else if (i < rating) {
          return const Icon(Icons.star_half_rounded,
              size: 13, color: AppColors.starColor);
        }
        return const Icon(Icons.star_outline_rounded,
            size: 13, color: AppColors.starColor);
      }),
    );
  }
}

class _ApplyButton extends StatelessWidget {
  const _ApplyButton({required this.job, required this.accentColor});
  final JobListing job;
  final Color accentColor;

  @override
  Widget build(BuildContext context) {
    if (job.isQuickApply) {
      return SizedBox(
        width: double.infinity,
        height: 42,
        child: ElevatedButton.icon(
          onPressed: () {},
          icon: const Icon(Icons.bolt_rounded, size: 16, color: Colors.white),
          label: const Text(
            'Quick Apply',
            style: TextStyle(
              fontFamily: 'DMSans',
              fontSize: 13.5,
              fontWeight: FontWeight.w700,
              color: Colors.white,
            ),
          ),
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.primaryGreen,
            foregroundColor: Colors.white,
            elevation: 0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(10),
            ),
          ),
        ),
      );
    }

    return SizedBox(
      width: double.infinity,
      height: 42,
      child: OutlinedButton(
        onPressed: () {},
        style: OutlinedButton.styleFrom(
          foregroundColor: accentColor,
          side: BorderSide(color: accentColor, width: 1.5),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
        ),
        child: const Text(
          'Apply Now',
          style: TextStyle(
            fontFamily: 'DMSans',
            fontSize: 13.5,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────── Bottom Nav ────────────────────────────

