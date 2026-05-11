import 'package:flutter/material.dart';

enum JobFilter { nearby, topPaying, urgent }

enum JobUrgencyType { todayOnly, daysLeft, open }

enum JobAccentColor { amber, green, purple, blue }

extension JobAccentColorExt on JobAccentColor {
  Color get color {
    switch (this) {
      case JobAccentColor.amber:
        return const Color(0xFFF59E0B);
      case JobAccentColor.green:
        return const Color(0xFF1A5C38);
      case JobAccentColor.purple:
        return const Color(0xFF7C3AED);
      case JobAccentColor.blue:
        return const Color(0xFF2563EB);
    }
  }
}

class JobTag {
  const JobTag({
    required this.label,
    required this.type,
  });

  final String label;
  final JobTagType type;
}

enum JobTagType { urgency, escrow, distance, category }

class JobListing {
  const JobListing({
    required this.id,
    required this.title,
    required this.employerName,
    required this.employerAvatarUrl,
    required this.locationName,
    required this.payKobo,
    required this.distanceKm,
    required this.rating,
    required this.reviewCount,
    required this.urgencyType,
    required this.daysLeft,
    required this.hasEscrow,
    required this.accentColor,
    required this.iconColor,
    required this.iconEmoji,
    required this.tags,
    required this.isQuickApply,
    required this.latitude,
    required this.longitude,
    required this.skillRequired,
  });

  final String id;
  final String title;
  final String employerName;
  final String? employerAvatarUrl;
  final String locationName;
  final int payKobo;
  final double distanceKm;
  final double rating;
  final int reviewCount;
  final JobUrgencyType urgencyType;
  final int? daysLeft;
  final bool hasEscrow;
  final JobAccentColor accentColor;
  final Color iconColor;
  final String iconEmoji;
  final List<JobTag> tags;
  final bool isQuickApply;
  final double latitude;
  final double longitude;
  final String skillRequired;

  String get distanceDisplay => '${distanceKm.toStringAsFixed(1)}km';

  String get urgencyLabel {
    switch (urgencyType) {
      case JobUrgencyType.todayOnly:
        return 'Today Only';
      case JobUrgencyType.daysLeft:
        return '${daysLeft ?? 0} days left';
      case JobUrgencyType.open:
        return 'Open';
    }
  }

  static List<JobListing> mockList() => [
        JobListing(
          id: 'j1',
          title: 'AC Technician Needed',
          employerName: 'ChillZone Lagos',
          employerAvatarUrl: null,
          locationName: 'Isale Eko, Lagos',
          payKobo: 850000,
          distanceKm: 1.2,
          rating: 4.5,
          reviewCount: 28,
          urgencyType: JobUrgencyType.todayOnly,
          daysLeft: null,
          hasEscrow: true,
          accentColor: JobAccentColor.amber,
          iconColor: const Color(0xFFF59E0B),
          iconEmoji: '❄️',
          tags: const [],
          isQuickApply: true,
          latitude: 6.4541,
          longitude: 3.3947,
          skillRequired: 'ac_technician',
        ),
        JobListing(
          id: 'j2',
          title: 'Van Driver – 2 Days',
          employerName: 'LogisticsPro',
          employerAvatarUrl: null,
          locationName: 'Victoria Island',
          payKobo: 1500000,
          distanceKm: 3.4,
          rating: 5.0,
          reviewCount: 42,
          urgencyType: JobUrgencyType.daysLeft,
          daysLeft: 2,
          hasEscrow: true,
          accentColor: JobAccentColor.green,
          iconColor: const Color(0xFF1A5C38),
          iconEmoji: '🚐',
          tags: const [],
          isQuickApply: true,
          latitude: 6.4281,
          longitude: 3.4219,
          skillRequired: 'driver',
        ),
        JobListing(
          id: 'j3',
          title: 'House Painter',
          employerName: 'HomeFixNG',
          employerAvatarUrl: null,
          locationName: 'Surulere, Lagos',
          payKobo: 1200000,
          distanceKm: 2.1,
          rating: 4.0,
          reviewCount: 16,
          urgencyType: JobUrgencyType.daysLeft,
          daysLeft: 5,
          hasEscrow: false,
          accentColor: JobAccentColor.purple,
          iconColor: const Color(0xFF7C3AED),
          iconEmoji: '🖌️',
          tags: const [],
          isQuickApply: false,
          latitude: 6.4968,
          longitude: 3.3507,
          skillRequired: 'painter',
        ),
      ];
}