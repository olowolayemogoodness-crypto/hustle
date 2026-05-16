import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:hustle/core/network/dio_client.dart';
import '../../../../core/config/theme.dart';
import '../../../../core/router/routes.dart';
import '../providers/auth_provider.dart';
import 'phone_auth_screen.dart'; // _GlowButton

class RoleSelectScreen extends ConsumerStatefulWidget {
  const RoleSelectScreen({super.key});

  @override
  ConsumerState<RoleSelectScreen> createState() => _RoleSelectScreenState();
}

class _RoleSelectScreenState extends ConsumerState<RoleSelectScreen> {
  String? _selected = 'worker'; // default worker selected as per design
  bool _loading = false;
// In role_select_screen.dart — update _continue()
Future<void> _continue() async {
  if (_selected == null) return;
  setState(() => _loading = true);

  try {
    // 1. Persist role in backend DB
    await DioClient.instance.post(
      '/api/v1/auth/role',
      data: {'role': _selected},
    );

    // 2. Update Supabase metadata + local state
    await ref.read(authProvider.notifier).setRole(_selected!);

  } catch (e) {
    if (mounted) {
      setState(() => _loading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed: $e')),
      );
    }
  }
}
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF6F6F6),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24),
          child: Column(
            children: [
              const SizedBox(height: 20),

              // ── Step indicator ──────────────────────────────────
              StepIndicator(current: 0, total: 3),

              const SizedBox(height: 28),

              // ── Title ───────────────────────────────────────────
              const Text(
                'Who are you?',
                style: TextStyle(
                  fontFamily: 'Syne',
                  fontSize: 30,
                  fontWeight: FontWeight.w800,
                  color: AppColors.textPrimary,
                ),
              ),
              const SizedBox(height: 6),
              const Text(
                'Choose how you want to use LocGig',
                style: TextStyle(
                  fontFamily: 'DMSans',
                  fontSize: 14,
                  color: AppColors.textSecondary,
                ),
              ),

              const SizedBox(height: 28),

              // ── App icon ─────────────────────────────────────────
              Container(
                width: 64,
                height: 64,
                decoration: BoxDecoration(
                  color: AppColors.primaryGreen,
                  borderRadius: BorderRadius.circular(18),
                ),
                child: const Icon(
                  Icons.location_on_rounded,
                  color: Colors.white,
                  size: 32,
                ),
              ),

              const SizedBox(height: 28),

              // ── Worker card ──────────────────────────────────────
              _RoleCard(
                role: 'worker',
                title: "I'm a Worker",
                subtitle: 'Find local jobs, apply instantly,\nget paid securely',
                iconBgColor: AppColors.primaryGreen,
                iconColor: Colors.white,
                icon: Icons.work_rounded,
                accentColor: AppColors.primaryGreen,
                isSelected: _selected == 'worker',
                onTap: () => setState(() => _selected = 'worker'),
              ),

              const SizedBox(height: 14),

              // ── Employer card ────────────────────────────────────
              _RoleCard(
                role: 'employer',
                title: "I'm an Employer",
                subtitle: 'Post jobs, hire trusted workers,\nmanage projects with escrow',
                iconBgColor: const Color(0xFFFEF3C7),
                iconColor: const Color(0xFFF59E0B),
                icon: Icons.domain_rounded,
                accentColor: const Color(0xFFF59E0B),
                isSelected: _selected == 'employer',
                onTap: () => setState(() => _selected = 'employer'),
              ),

              const SizedBox(height: 24),

              // ── Feature pills ────────────────────────────────────
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: const [
                  _FeaturePill(
                    icon: Icons.shield_outlined,
                    label: 'Escrow\nProtected',
                  ),
                  SizedBox(width: 10),
                  _FeaturePill(
                    icon: Icons.star_rounded,
                    label: 'Trust Score',
                    iconColor: Color(0xFFF59E0B),
                  ),
                  SizedBox(width: 10),
                  _FeaturePill(
                    icon: Icons.location_on_outlined,
                    label: 'Near You',
                  ),
                ],
              ),

              const Spacer(),

              // ── Continue button ──────────────────────────────────
              GlowButton(
                onPressed: (_selected == null || _loading) ? null : _continue,
                loading: _loading,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: const [
                    Text(
                      'Continue',
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

              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────── Role Card ────────────────────────────────────

class _RoleCard extends StatelessWidget {
  const _RoleCard({
    required this.role,
    required this.title,
    required this.subtitle,
    required this.iconBgColor,
    required this.iconColor,
    required this.icon,
    required this.accentColor,
    required this.isSelected,
    required this.onTap,
  });

  final String role, title, subtitle;
  final Color iconBgColor, iconColor, accentColor;
  final IconData icon;
  final bool isSelected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        decoration: BoxDecoration(
          color: isSelected
              ? const Color(0xFFEDF8F1)
              : Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isSelected ? accentColor : const Color(0xFFE5E7EB),
            width: isSelected ? 2 : 1.5,
          ),
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(14),
          child: IntrinsicHeight(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Left accent bar (only on unselected employer)
                if (!isSelected && role == 'employer')
                  Container(width: 4, color: accentColor),

                Expanded(
                  child: Padding(
                    padding: EdgeInsets.fromLTRB(
                      !isSelected && role == 'employer' ? 12 : 16,
                      16, 16, 16,
                    ),
                    child: Row(
                      children: [
                        // Icon circle
                        Container(
                          width: 46,
                          height: 46,
                          decoration: BoxDecoration(
                            color: iconBgColor,
                            shape: BoxShape.circle,
                          ),
                          child: Icon(icon, color: iconColor, size: 22),
                        ),

                        const SizedBox(width: 14),

                        // Text
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(
                                title,
                                style: const TextStyle(
                                  fontFamily: 'DMSans',
                                  fontSize: 16,
                                  fontWeight: FontWeight.w700,
                                  color: AppColors.textPrimary,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                subtitle,
                                style: const TextStyle(
                                  fontFamily: 'DMSans',
                                  fontSize: 12.5,
                                  color: AppColors.textSecondary,
                                  height: 1.5,
                                ),
                              ),
                            ],
                          ),
                        ),

                        const SizedBox(width: 12),

                        // Radio / Checkmark
                        AnimatedSwitcher(
                          duration: const Duration(milliseconds: 200),
                          child: isSelected
                              ? Container(
                                  key: const ValueKey('checked'),
                                  width: 26,
                                  height: 26,
                                  decoration: BoxDecoration(
                                    color: accentColor,
                                    shape: BoxShape.circle,
                                  ),
                                  child: const Icon(
                                    Icons.check_rounded,
                                    color: Colors.white,
                                    size: 16,
                                  ),
                                )
                              : Container(
                                  key: const ValueKey('unchecked'),
                                  width: 26,
                                  height: 26,
                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    border: Border.all(
                                      color: const Color(0xFFD1D5DB),
                                      width: 2,
                                    ),
                                  ),
                                ),
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
}

// ─────────────────────────── Feature Pill ─────────────────────────────────

class _FeaturePill extends StatelessWidget {
  const _FeaturePill({
    required this.icon,
    required this.label,
    this.iconColor = AppColors.primaryGreen,
  });

  final IconData icon;
  final String label;
  final Color iconColor;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE5E7EB), width: 1.2),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: iconColor),
          const SizedBox(width: 5),
          Text(
            label,
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontFamily: 'DMSans',
              fontSize: 11.5,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
              height: 1.3,
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────── Step Indicator ───────────────────────────────

class StepIndicator extends StatelessWidget {
  const StepIndicator({required this.current, required this.total});
  final int current;
  final int total;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: List.generate(total, (i) {
        final isActive = i == current;
        return AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          margin: const EdgeInsets.symmetric(horizontal: 3),
          width: isActive ? 28 : 8,
          height: 8,
          decoration: BoxDecoration(
            color: isActive
                ? AppColors.primaryGreen
                : const Color(0xFFD1D5DB),
            borderRadius: BorderRadius.circular(4),
          ),
        );
      }),
    );
  }
}



/// Reusable green pill button with bottom glow
class GlowButton extends StatelessWidget {
  const GlowButton({
    required this.child,
    required this.onPressed,
    this.loading = false,
  });

  final Widget child;
  final VoidCallback? onPressed;
  final bool loading;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 54,
      width: double.infinity,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(30),
        boxShadow: [
          BoxShadow(
            color: AppColors.primaryGreen.withOpacity(0.35),
            blurRadius: 20,
            offset: const Offset(0, 8),
            spreadRadius: -4,
          ),
        ],
      ),
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primaryGreen,
          disabledBackgroundColor: AppColors.primaryGreen.withOpacity(0.5),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(30),
          ),
          elevation: 0,
        ),
        child: loading
            ? const SizedBox(
                width: 22,
                height: 22,
                child: CircularProgressIndicator(
                  color: Colors.white,
                  strokeWidth: 2.5,
                ),
              )
            : child,
      ),
    );
  }
}
