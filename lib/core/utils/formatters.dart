import 'package:intl/intl.dart';

class Formatters {
  Formatters._();

  /// Formats kobo (integer) to Naira display string: ₦8,500.00
  static String naira(int kobo) {
    final naira = kobo / 100;
    final formatter = NumberFormat('#,##0.00', 'en_NG');
    return '₦${formatter.format(naira)}';
  }

  /// Compact naira: ₦4.5k, ₦1.2m
  static String nairaCompact(int kobo) {
    final naira = kobo / 100;
    if (naira >= 1000000) {
      return '₦${(naira / 1000000).toStringAsFixed(1)}m';
    } else if (naira >= 1000) {
      return '₦${(naira / 1000).toStringAsFixed(1)}k';
    }
    return '₦${naira.toStringAsFixed(0)}';
  }

  /// Format date to "Jan 15"
  static String shortDate(DateTime date) {
    return DateFormat('MMM d').format(date);
  }

  /// Format date to "Jan 2024"
  static String monthYear(DateTime date) {
    return DateFormat('MMM yyyy').format(date);
  }
}