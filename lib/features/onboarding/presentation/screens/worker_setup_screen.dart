import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/config/theme.dart';
import '../../../../core/router/routes.dart';
// _GlowButton, _CircleBackButton
import '../../../auth/presentation/screens/role_select_screen.dart' ; // _StepIndicator
// ── Skill model ──────────────────────────────────────────────────────────

class _Skill {
  const _Skill(this.label, this.icon);
  final String label;
  final IconData icon;
}

const _kSkills = [
  _Skill('Plumber',        Icons.plumbing_rounded),
  _Skill('Electrician',    Icons.electric_bolt_rounded),
  _Skill('Driver',         Icons.drive_eta_rounded),
  _Skill('Carpenter',      Icons.handyman_rounded),
  _Skill('Painter',        Icons.format_paint_rounded),
  _Skill('Security Guard', Icons.security_rounded),
  _Skill('Cleaner',        Icons.cleaning_services_rounded),
  _Skill('Delivery',       Icons.local_shipping_rounded),
  _Skill('Chef',           Icons.restaurant_rounded),
  _Skill('IT Repair',      Icons.laptop_rounded),
  _Skill('Mason',          Icons.construction_rounded),
  _Skill('Tailor',         Icons.content_cut_rounded),
];

const _kJobTypes = ['Full Day', 'Part Time', 'Quick Task'];

// ── Screen ────────────────────────────────────────────────────────────────

class WorkerSetupScreen extends ConsumerStatefulWidget {
  const WorkerSetupScreen({super.key});

  @override
  ConsumerState<WorkerSetupScreen> createState() => _WorkerSetupScreenState();
}

class _WorkerSetupScreenState extends ConsumerState<WorkerSetupScreen> {
  final Set<String> _selectedSkills = {'Plumber', 'Electrician', 'Driver', 'Cleaner'};
  double _radiusKm = 5;
  int _jobTypeIndex = 0;
  bool _loading = false;

  Future<void> _complete() async {
    if (_selectedSkills.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select at least one skill')),
      );
      return;
    }
    setState(() => _loading = true);
    // TODO: POST to /api/v1/workers/me with skills + radius + job_type
    await Future.delayed(const Duration(milliseconds: 800));
    if (mounted) context.go(Routes.discovery);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Column(
          children: [
            // ── Scrollable body ────────────────────────────────────
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const SizedBox(height: 16),

                    // Back + step indicator row
                    Row(
                      children: [
                        CircleBackButton(),
                        const SizedBox(width: 16),
                        StepIndicator(current: 2, total: 3),
                      ],
                    ),

                    const SizedBox(height: 24),

                    // ── Title ──────────────────────────────────────
                    const Text(
                      'Set Up Your Profile',
                      style: TextStyle(
                        fontFamily: 'Syne',
                        fontSize: 26,
                        fontWeight: FontWeight.w800,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 6),
                    const Text(
                      'Select your skills — pick all that apply',
                      style: TextStyle(
                        fontFamily: 'DMSans',
                        fontSize: 14,
                        color: AppColors.textSecondary,
                      ),
                    ),

                    const SizedBox(height: 24),

                    // ── Photo upload ───────────────────────────────
                    Center(child: _PhotoUploadCircle()),

                    const SizedBox(height: 24),

                    // ── Skills grid ────────────────────────────────
                    Wrap(
                      spacing: 8,
                      runSpacing: 10,
                      children: _kSkills.map((skill) {
                        final isSelected = _selectedSkills.contains(skill.label);
                        return _SkillChip(
                          skill: skill,
                          isSelected: isSelected,
                          onTap: () {
                            setState(() {
                              isSelected
                                  ? _selectedSkills.remove(skill.label)
                                  : _selectedSkills.add(skill.label);
                            });
                          },
                        );
                      }).toList(),
                    ),

                    const SizedBox(height: 24),

                    // ── Location radius ────────────────────────────
                    _RadiusCard(
                      value: _radiusKm,
                      onChanged: (v) => setState(() => _radiusKm = v),
                    ),

                    const SizedBox(height: 22),

                    // ── Preferred job types ────────────────────────
                    const Text(
                      'Preferred Job Types',
                      style: TextStyle(
                        fontFamily: 'DMSans',
                        fontSize: 15,
                        fontWeight: FontWeight.w700,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 10),
                    _JobTypeSelector(
                      options: _kJobTypes,
                      selected: _jobTypeIndex,
                      onSelect: (i) => setState(() => _jobTypeIndex = i),
                    ),

                    const SizedBox(height: 32),
                  ],
                ),
              ),
            ),

            // ── Complete Setup button ──────────────────────────────
            Padding(
              padding: const EdgeInsets.fromLTRB(24, 8, 24, 24),
              child: GlowButton(
                onPressed: _loading ? null : _complete,
                loading: _loading,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: const [
                    Text(
                      'Complete Setup',
                      style: TextStyle(
                        fontFamily: 'DMSans',
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        color: Colors.white,
                      ),
                    ),
                    SizedBox(width: 8),
                    Icon(Icons.arrow_forward_rounded,
                        color: Colors.white, size: 18),
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

// ─────────────────────────── Photo Upload Circle ──────────────────────────

class _PhotoUploadCircle extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        // TODO: image_picker integration
      },
      child: SizedBox(
        width: 88,
        height: 88,
        child: Stack(
          alignment: Alignment.center,
          children: [
            // Dashed border
            CustomPaint(
              size: const Size(88, 88),
              painter: _DashedCirclePainter(
                color: AppColors.primaryGreen,
                strokeWidth: 1.8,
                dashCount: 22,
              ),
            ),
            // Content
            Column(
              mainAxisSize: MainAxisSize.min,
              children: const [
                Icon(
                  Icons.camera_alt_outlined,
                  color: AppColors.primaryGreen,
                  size: 26,
                ),
                SizedBox(height: 4),
                Text(
                  'Upload',
                  style: TextStyle(
                    fontFamily: 'DMSans',
                    fontSize: 11.5,
                    fontWeight: FontWeight.w600,
                    color: AppColors.primaryGreen,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _DashedCirclePainter extends CustomPainter {
  const _DashedCirclePainter({
    required this.color,
    required this.strokeWidth,
    required this.dashCount,
  });

  final Color color;
  final double strokeWidth;
  final int dashCount;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = strokeWidth
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width / 2) - strokeWidth;
    final total = 2 * math.pi;
    final dashAngle = total / dashCount;
    const gapRatio = 0.38;

    for (var i = 0; i < dashCount; i++) {
      final start = i * dashAngle;
      final sweep = dashAngle * (1 - gapRatio);
      canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        start,
        sweep,
        false,
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(_) => false;
}

// ─────────────────────────── Skill Chip ───────────────────────────────────

class _SkillChip extends StatelessWidget {
  const _SkillChip({
    required this.skill,
    required this.isSelected,
    required this.onTap,
  });

  final _Skill skill;
  final bool isSelected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 9),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.primaryGreen : Colors.white,
          borderRadius: BorderRadius.circular(30),
          border: Border.all(
            color: isSelected
                ? AppColors.primaryGreen
                : const Color(0xFFD1D5DB),
            width: 1.5,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              skill.icon,
              size: 14,
              color: isSelected ? Colors.white : AppColors.textSecondary,
            ),
            const SizedBox(width: 6),
            Text(
              skill.label,
              style: TextStyle(
                fontFamily: 'DMSans',
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: isSelected ? Colors.white : AppColors.textPrimary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────── Radius Card ──────────────────────────────────

class _RadiusCard extends StatelessWidget {
  const _RadiusCard({required this.value, required this.onChanged});
  final double value;
  final ValueChanged<double> onChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 10),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE5E7EB), width: 1.5),
      ),
      child: Column(
        children: [
          // Label + value row
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: const [
                  Icon(
                    Icons.location_on_rounded,
                    size: 16,
                    color: AppColors.primaryGreen,
                  ),
                  SizedBox(width: 6),
                  Text(
                    'Location Radius',
                    style: TextStyle(
                      fontFamily: 'DMSans',
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: AppColors.textPrimary,
                    ),
                  ),
                ],
              ),
              Text(
                '${value.toInt()} km',
                style: const TextStyle(
                  fontFamily: 'Syne',
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: AppColors.primaryGreen,
                ),
              ),
            ],
          ),

          const SizedBox(height: 6),

          // Slider
          SliderTheme(
            data: SliderTheme.of(context).copyWith(
              activeTrackColor: AppColors.primaryGreen,
              inactiveTrackColor: const Color(0xFFE5E7EB),
              thumbColor: AppColors.primaryGreen,
              overlayColor: AppColors.primaryGreen.withOpacity(0.12),
              trackHeight: 4,
              thumbShape:
                  const RoundSliderThumbShape(enabledThumbRadius: 10),
              overlayShape:
                  const RoundSliderOverlayShape(overlayRadius: 20),
            ),
            child: Slider(
              value: value,
              min: 1,
              max: 20,
              divisions: 19,
              onChanged: onChanged,
            ),
          ),

          // Min / Max labels
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 4),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: const [
                Text('1 km',
                    style: TextStyle(
                        fontFamily: 'DMSans',
                        fontSize: 11,
                        color: AppColors.textSecondary)),
                Text('20 km',
                    style: TextStyle(
                        fontFamily: 'DMSans',
                        fontSize: 11,
                        color: AppColors.textSecondary)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────── Job Type Selector ────────────────────────────

class _JobTypeSelector extends StatelessWidget {
  const _JobTypeSelector({
    required this.options,
    required this.selected,
    required this.onSelect,
  });

  final List<String> options;
  final int selected;
  final ValueChanged<int> onSelect;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 46,
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: const Color(0xFFF3F4F6),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: List.generate(options.length, (i) {
          final isActive = i == selected;
          return Expanded(
            child: GestureDetector(
              onTap: () => onSelect(i),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: isActive ? AppColors.primaryGreen : Colors.transparent,
                  borderRadius: BorderRadius.circular(9),
                  boxShadow: isActive
                      ? [
                          BoxShadow(
                            color: AppColors.primaryGreen.withOpacity(0.25),
                            blurRadius: 6,
                            offset: const Offset(0, 2),
                          ),
                        ]
                      : null,
                ),
                child: Text(
                  options[i],
                  style: TextStyle(
                    fontFamily: 'DMSans',
                    fontSize: 13,
                    fontWeight:
                        isActive ? FontWeight.w700 : FontWeight.w500,
                    color: isActive ? Colors.white : AppColors.textSecondary,
                  ),
                ),
              ),
            ),
          );
        }),
      ),
    );
  }
}

class CircleBackButton extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => context.canPop() ? context.pop() : null,
      child: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: const Color(0xFFF2F2F2),
          shape: BoxShape.circle,
        ),
        child: const Icon(
          Icons.arrow_back_rounded,
          size: 20,
          color: AppColors.textPrimary,
        ),
      ),
    );
  }
}