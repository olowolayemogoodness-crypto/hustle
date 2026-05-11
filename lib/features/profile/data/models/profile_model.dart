class WorkerProfile {
  const WorkerProfile({
    required this.id,
    required this.fullName,
    required this.avatarUrl,
    required this.skills,
    required this.primarySkills,
    required this.location,
    required this.joinedAt,
    required this.totalJobs,
    required this.trustScore,
    required this.completionRate,
    required this.disputesCount,
    required this.ratingsCount,
    required this.isVerified,
    required this.topPercentile,
    required this.reviews,
  });

  final String id;
  final String fullName;
  final String? avatarUrl;
  final List<String> skills;
  final List<String> primarySkills; // shown in subtitle
  final String location;
  final DateTime joinedAt;
  final int totalJobs;
  final double trustScore;
  final double completionRate; // 0.0 - 1.0
  final int disputesCount;
  final int ratingsCount;
  final bool isVerified;
  final String topPercentile; // e.g. "Top 10% in Lagos"
  final List<WorkerReview> reviews;

  String get primarySkillsDisplay => primarySkills.join(' · ');

  factory WorkerProfile.mock() => WorkerProfile(
        id: 'worker-001',
        fullName: 'Emeka Okafor',
        avatarUrl: null, // placeholder
        skills: const ['Electrician', 'Plumber', 'Driver', 'Carpenter'],
        primarySkills: const ['Electrician', 'Plumber', 'Driver'],
        location: 'Lagos, Mainland',
        joinedAt: DateTime(2024, 1, 1),
        totalJobs: 14,
        trustScore: 4.8,
        completionRate: 1.0,
        disputesCount: 0,
        ratingsCount: 14,
        isVerified: true,
        topPercentile: 'Top 10% in Lagos',
        reviews: [
          WorkerReview(
            id: 'r1',
            reviewerName: 'ChillZone Lagos',
            reviewerAvatarUrl: null,
            rating: 5.0,
            comment: 'Excellent work, very punctual! Would definitely hire again.',
            date: DateTime(2024, 1, 15),
          ),
          WorkerReview(
            id: 'r2',
            reviewerName: 'HomeFixNG',
            reviewerAvatarUrl: null,
            rating: 4.0,
            comment: 'Showed up on time, good skills. Finished the job cleanly.',
            date: DateTime(2024, 1, 8),
          ),
        ],
      );
}

class WorkerReview {
  const WorkerReview({
    required this.id,
    required this.reviewerName,
    required this.reviewerAvatarUrl,
    required this.rating,
    required this.comment,
    required this.date,
  });

  final String id;
  final String reviewerName;
  final String? reviewerAvatarUrl;
  final double rating;
  final String comment;
  final DateTime date;
}