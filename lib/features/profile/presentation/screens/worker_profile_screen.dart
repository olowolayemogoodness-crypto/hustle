import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../../../core/config/theme.dart';
import '../../../../core/utils/formatters.dart';
import '../../../../shared/widgets/skill_chip.dart';
import '../../data/models/profile_model.dart';
import '../providers/profile_provider.dart';

class WorkerProfileScreen extends ConsumerWidget {
  const WorkerProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileAsync = ref.watch(profileProvider);

    return Scaffold(
      backgroundColor: AppColors.backgroundWhite,
      appBar: AppBar(
        backgroundColor: AppColors.backgroundWhite,
        elevation: 0,
        centerTitle: true,
        title: const Text(
          'Profile',
          style: TextStyle(
            fontFamily: 'DMSans',
            fontSize: 18,
            fontWeight: FontWeight.w700,
            color: AppColors.textPrimary,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit_outlined, color: AppColors.textPrimary, size: 22),
            onPressed: () {},
          ),
          IconButton(
            icon: const Icon(Icons.settings_outlined, color: AppColors.textPrimary, size: 22),
            onPressed: () {},
          ),
        ],
      ),
      body: profileAsync.when(
        loading: () => const Center(
          child: CircularProgressIndicator(color: AppColors.primaryGreen),
        ),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (profile) => RefreshIndicator(
          color: AppColors.primaryGreen,
          onRefresh: () => ref.read(profileProvider.notifier).refresh(),
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 8),
                _ProfileHeader(profile: profile),
                const SizedBox(height: 14),
                _TrustScoreCard(profile: profile),
                const SizedBox(height: 20),
                _SkillsSection(skills: profile.skills),
                const SizedBox(height: 20),
                _ReviewsSection(reviews: profile.reviews),
                const SizedBox(height: 20),
                _VerificationSection(isVerified: profile.isVerified),
                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────── Profile Header ────────────────────────────

class _ProfileHeader extends StatelessWidget {
  const _ProfileHeader({required this.profile});
  final WorkerProfile profile;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 22, horizontal: 18),
      decoration: BoxDecoration(
        color: AppColors.primaryGreenLight,
        borderRadius: BorderRadius.circular(18),
      ),
      child: Column(
        children: [
          Stack(
            alignment: Alignment.bottomRight,
            children: [
              CircleAvatar(
                radius: 42,
                backgroundColor: AppColors.borderLight,
                backgroundImage: profile.avatarUrl != null
                    ? NetworkImage(profile.avatarUrl!)
                    : null,
                child: profile.avatarUrl == null
                    ? Text(
                        profile.fullName[0],
                        style: const TextStyle(
                          fontFamily: 'Syne',
                          fontSize: 30,
                          fontWeight: FontWeight.w700,
                          color: AppColors.primaryGreen,
                        ),
                      )
                    : null,
              ),
              Container(
                width: 22,
                height: 22,
                decoration: const BoxDecoration(
                  color: AppColors.primaryGreen,
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.check, color: Colors.white, size: 14),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            profile.fullName,
            style: const TextStyle(
              fontFamily: 'Syne',
              fontSize: 20,
              fontWeight: FontWeight.w700,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 4),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text('⚡', style: TextStyle(fontSize: 13)),
              const SizedBox(width: 3),
              Text(
                profile.primarySkillsDisplay,
                style: const TextStyle(
                  fontFamily: 'DMSans',
                  fontSize: 13,
                  fontWeight: FontWeight.w500,
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 5),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.location_on_outlined,
                  size: 14, color: AppColors.textSecondary),
              const SizedBox(width: 2),
              Text(
                profile.location,
                style: const TextStyle(
                  fontFamily: 'DMSans',
                  fontSize: 13,
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            'Joined ${DateFormat('MMM yyyy').format(profile.joinedAt)} · ${profile.totalJobs} jobs completed',
            style: const TextStyle(
              fontFamily: 'DMSans',
              fontSize: 12,
              color: AppColors.textHint,
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────── Trust Score Card ────────────────────────────

class _TrustScoreCard extends StatelessWidget {
  const _TrustScoreCard({required this.profile});
  final WorkerProfile profile;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Trust Score',
                style: TextStyle(
                  fontFamily: 'DMSans',
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textPrimary,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                decoration: BoxDecoration(
                  color: AppColors.primaryGreenLight,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.emoji_events_outlined,
                        size: 13, color: AppColors.primaryGreen),
                    const SizedBox(width: 4),
                    Text(
                      profile.topPercentile,
                      style: const TextStyle(
                        fontFamily: 'DMSans',
                        fontSize: 11.5,
                        fontWeight: FontWeight.w600,
                        color: AppColors.primaryGreen,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              _TrustScoreCircle(score: profile.trustScore),
              const SizedBox(width: 20),
              Expanded(
                child: _TrustStatsGrid(profile: profile),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _TrustScoreCircle extends StatelessWidget {
  const _TrustScoreCircle({required this.score});
  final double score;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 84,
      height: 84,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(color: AppColors.primaryGreen, width: 4),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            score.toStringAsFixed(1),
            style: const TextStyle(
              fontFamily: 'Syne',
              fontSize: 26,
              fontWeight: FontWeight.w800,
              color: AppColors.primaryGreen,
              height: 1,
            ),
          ),
          const Text(
            '/ 5.0',
            style: TextStyle(
              fontFamily: 'DMSans',
              fontSize: 11,
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }
}

class _TrustStatsGrid extends StatelessWidget {
  const _TrustStatsGrid({required this.profile});
  final WorkerProfile profile;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: _TrustStat(
                label: 'Completion',
                value: '${(profile.completionRate * 100).toInt()}%',
                valueColor: AppColors.primaryGreen,
              ),
            ),
            Expanded(
              child: _TrustStat(
                label: 'Disputes',
                value: '${profile.disputesCount}',
              ),
            ),
          ],
        ),
        const SizedBox(height: 14),
        Row(
          children: [
            Expanded(
              child: _TrustStat(
                label: 'Ratings',
                value: '${profile.ratingsCount}',
              ),
            ),
            Expanded(
              child: _TrustStat(
                label: 'Status',
                value: profile.isVerified ? 'Verified ✓' : 'Unverified',
                valueColor:
                    profile.isVerified ? AppColors.primaryGreen : AppColors.accentRed,
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _TrustStat extends StatelessWidget {
  const _TrustStat({
    required this.label,
    required this.value,
    this.valueColor = AppColors.textPrimary,
  });
  final String label;
  final String value;
  final Color valueColor;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontFamily: 'DMSans',
            fontSize: 11.5,
            color: AppColors.textSecondary,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          value,
          style: TextStyle(
            fontFamily: 'DMSans',
            fontSize: 15,
            fontWeight: FontWeight.w700,
            color: valueColor,
          ),
        ),
      ],
    );
  }
}

// ─────────────────────────── Skills Section ────────────────────────────

class _SkillsSection extends StatelessWidget {
  const _SkillsSection({required this.skills});
  final List<String> skills;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Skills',
          style: TextStyle(
            fontFamily: 'DMSans',
            fontSize: 16,
            fontWeight: FontWeight.w700,
            color: AppColors.textPrimary,
          ),
        ),
        const SizedBox(height: 10),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: skills.asMap().entries.map((e) {
            final isFilled = e.key < 2;
            return SkillChip(
              label: e.value,
              variant: isFilled
                  ? SkillChipVariant.filled
                  : SkillChipVariant.outlined,
            );
          }).toList(),
        ),
      ],
    );
  }
}

// ─────────────────────────── Reviews Section ────────────────────────────

class _ReviewsSection extends StatelessWidget {
  const _ReviewsSection({required this.reviews});
  final List<WorkerReview> reviews;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Recent Reviews',
          style: TextStyle(
            fontFamily: 'DMSans',
            fontSize: 16,
            fontWeight: FontWeight.w700,
            color: AppColors.textPrimary,
          ),
        ),
        const SizedBox(height: 12),
        ...reviews.map((review) => _ReviewCard(review: review)),
      ],
    );
  }
}

class _ReviewCard extends StatelessWidget {
  const _ReviewCard({required this.review});
  final WorkerReview review;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppColors.borderLight),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 18,
                backgroundColor: AppColors.primaryGreenLight,
                backgroundImage: review.reviewerAvatarUrl != null
                    ? NetworkImage(review.reviewerAvatarUrl!)
                    : null,
                child: review.reviewerAvatarUrl == null
                    ? Text(
                        review.reviewerName[0],
                        style: const TextStyle(
                          fontFamily: 'DMSans',
                          fontSize: 14,
                          fontWeight: FontWeight.w700,
                          color: AppColors.primaryGreen,
                        ),
                      )
                    : null,
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      review.reviewerName,
                      style: const TextStyle(
                        fontFamily: 'DMSans',
                        fontSize: 13.5,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    _StarRating(rating: review.rating),
                  ],
                ),
              ),
              Text(
                Formatters.shortDate(review.date),
                style: const TextStyle(
                  fontFamily: 'DMSans',
                  fontSize: 11.5,
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            '"${review.comment}"',
            style: const TextStyle(
              fontFamily: 'DMSans',
              fontSize: 12.5,
              color: AppColors.textSecondary,
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }
}

class _StarRating extends StatelessWidget {
  const _StarRating({required this.rating});
  final double rating;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: List.generate(5, (i) {
        if (i < rating.floor()) {
          return const Icon(Icons.star_rounded, size: 14, color: AppColors.starColor);
        } else if (i < rating) {
          return const Icon(Icons.star_half_rounded, size: 14, color: AppColors.starColor);
        } else {
          return const Icon(Icons.star_outline_rounded, size: 14, color: AppColors.starColor);
        }
      }),
    );
  }
}

// ─────────────────────────── Verification Section ────────────────────────────

class _VerificationSection extends StatelessWidget {
  const _VerificationSection({required this.isVerified});
  final bool isVerified;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Verification',
          style: TextStyle(
            fontFamily: 'DMSans',
            fontSize: 16,
            fontWeight: FontWeight.w700,
            color: AppColors.textPrimary,
          ),
        ),
        const SizedBox(height: 10),
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: isVerified
                ? AppColors.primaryGreenLight
                : AppColors.backgroundGrey,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
              color: isVerified
                  ? AppColors.primaryGreen.withOpacity(0.3)
                  : AppColors.borderLight,
            ),
          ),
          child: Row(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: isVerified ? AppColors.primaryGreen : AppColors.borderLight,
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  isVerified ? Icons.verified_user_rounded : Icons.person_outline,
                  color: Colors.white,
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      isVerified ? 'NIN Verified' : 'NIN Not Linked',
                      style: TextStyle(
                        fontFamily: 'DMSans',
                        fontSize: 13.5,
                        fontWeight: FontWeight.w600,
                        color: isVerified
                            ? AppColors.primaryGreen
                            : AppColors.textPrimary,
                      ),
                    ),
                    Text(
                      isVerified
                          ? 'Your identity has been verified'
                          : 'Link your NIN to boost trust score',
                      style: const TextStyle(
                        fontFamily: 'DMSans',
                        fontSize: 12,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              if (!isVerified)
                GestureDetector(
                  onTap: () {},
                  child: const Text(
                    'Verify →',
                    style: TextStyle(
                      fontFamily: 'DMSans',
                      fontSize: 12.5,
                      fontWeight: FontWeight.w600,
                      color: AppColors.primaryGreen,
                    ),
                  ),
                ),
            ],
          ),
        ),
      ],
    );
  }
}