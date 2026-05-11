import 'package:flutter/material.dart';
import '../../core/config/theme.dart';

enum SkillChipVariant { filled, outlined }

class SkillChip extends StatelessWidget {
  const SkillChip({
    super.key,
    required this.label,
    this.variant = SkillChipVariant.filled,
    this.onTap,
  });

  final String label;
  final SkillChipVariant variant;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final isFilled = variant == SkillChipVariant.filled;
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: isFilled ? AppColors.primaryGreen : Colors.transparent,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: AppColors.primaryGreen,
            width: 1.5,
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontFamily: 'DMSans',
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: isFilled ? Colors.white : AppColors.primaryGreen,
          ),
        ),
      ),
    );
  }
}