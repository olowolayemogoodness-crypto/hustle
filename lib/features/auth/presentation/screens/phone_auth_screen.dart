import 'package:flutter/material.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/config/theme.dart';
import '../../../../core/router/routes.dart';
import '../providers/auth_provider.dart';

class PhoneAuthScreen extends ConsumerStatefulWidget {
  const PhoneAuthScreen({super.key});

  @override
  ConsumerState<PhoneAuthScreen> createState() => _PhoneAuthScreenState();
}

class _PhoneAuthScreenState extends ConsumerState<PhoneAuthScreen> {
  final _ctrl   = TextEditingController();
  final _form   = GlobalKey<FormState>();
  bool _loading = false;

  String get _normalisedPhone {
    var v = _ctrl.text.trim().replaceAll(' ', '').replaceAll('-', '');
    if (v.startsWith('0') && v.length == 11) v = '+234${v.substring(1)}';
    if (v.startsWith('234') && !v.startsWith('+')) v = '+$v';
    if (!v.startsWith('+')) v = '+234$v';
    return v;
  }

  Future<void> _submit() async {
    if (!(_form.currentState?.validate() ?? false)) return;
    setState(() => _loading = true);
    try {
      await ref.read(authProvider.notifier).sendOtp(_normalisedPhone);
      if (mounted) context.push(Routes.otp, extra: _normalisedPhone);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.toString()), backgroundColor: AppColors.accentRed),
        );
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24),
          child: Form(
            key: _form,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 16),

                // ── Back button ──────────────────────────────────────
                CircleBackButton(),

                const SizedBox(height: 28),

                // ── Title ────────────────────────────────────────────
                const Text(
                  'Welcome to LocGig',
                  style: TextStyle(
                    fontFamily: 'Syne',
                    fontSize: 28,
                    fontWeight: FontWeight.w800,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 6),
                const Text(
                  'Enter your phone number to get started',
                  style: TextStyle(
                    fontFamily: 'DMSans',
                    fontSize: 14,
                    color: AppColors.textSecondary,
                  ),
                ),

                const SizedBox(height: 32),

                // ── Country & Code label ─────────────────────────────
                const _FieldLabel('Country & Code'),
                const SizedBox(height: 8),

                // ── Country selector ─────────────────────────────────
                _CountryField(),

                const SizedBox(height: 16),

                // ── Phone Number label ───────────────────────────────
                const _FieldLabel('Phone Number'),
                const SizedBox(height: 8),

                // ── Phone input ──────────────────────────────────────
                Container(
                  height: 54,
                  decoration: BoxDecoration(
                    color: AppColors.backgroundGrey,
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: Row(
                    children: [
                      const SizedBox(width: 16),
                      Icon(
                        Icons.phone_outlined,
                        size: 20,
                        color: AppColors.primaryGreen.withOpacity(0.7),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: TextFormField(
                          controller: _ctrl,
                          keyboardType: TextInputType.phone,
                          style: const TextStyle(
                            fontFamily: 'DMSans',
                            fontSize: 16,
                            color: AppColors.textPrimary,
                            letterSpacing: 0.5,
                          ),
                          decoration: const InputDecoration(
                            hintText: '803 000 0000',
                            hintStyle: TextStyle(
                              color: AppColors.textHint,
                              fontSize: 15,
                              letterSpacing: 0.5,
                            ),
                            border: InputBorder.none,
                            isDense: true,
                            contentPadding: EdgeInsets.zero,
                          ),
                          validator: (v) {
                            final n = v?.trim().replaceAll(' ', '') ?? '';
                            if (n.isEmpty) return 'Enter your phone number';
                            if (n.length < 7) return 'Invalid phone number';
                            return null;
                          },
                        ),
                      ),
                      const SizedBox(width: 14),
                    ],
                  ),
                ),

                const SizedBox(height: 18),

                // ── Terms text ───────────────────────────────────────
                Center(
                  child: RichText(
                    textAlign: TextAlign.center,
                    text: TextSpan(
                      style: const TextStyle(
                        fontFamily: 'DMSans',
                        fontSize: 12.5,
                        color: AppColors.textSecondary,
                        height: 1.6,
                      ),
                      children: [
                        const TextSpan(text: 'By continuing, you agree to our '),
                        TextSpan(
                          text: 'Terms of Service',
                          style: const TextStyle(
                            color: AppColors.primaryGreen,
                            fontWeight: FontWeight.w600,
                          ),
                          recognizer: TapGestureRecognizer()..onTap = () {},
                        ),
                        const TextSpan(text: ' & '),
                        TextSpan(
                          text: 'Privacy Policy',
                          style: const TextStyle(
                            color: AppColors.primaryGreen,
                            fontWeight: FontWeight.w600,
                          ),
                          recognizer: TapGestureRecognizer()..onTap = () {},
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 24),

                // ── Continue button ──────────────────────────────────
                GlowButton(
                  onPressed: _loading ? null : _submit,
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

                // ── Divider ──────────────────────────────────────────
                Row(
                  children: [
                    Expanded(
                      child: Divider(color: AppColors.borderLight, thickness: 1),
                    ),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 12),
                      child: Text(
                        'or continue with',
                        style: TextStyle(
                          fontFamily: 'DMSans',
                          fontSize: 13,
                          color: AppColors.textSecondary.withOpacity(0.7),
                        ),
                      ),
                    ),
                    Expanded(
                      child: Divider(color: AppColors.borderLight, thickness: 1),
                    ),
                  ],
                ),

                const SizedBox(height: 16),

                // ── Google sign-in ───────────────────────────────────
                GestureDetector(
                  onTap: () {
                    // TODO: wire up Google Sign-In (google_sign_in package)
                  },
                  child: Container(
                    height: 54,
                    width: double.infinity,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(30),
                      border: Border.all(
                        color: AppColors.borderLight,
                        width: 1.5,
                      ),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        _GoogleLogo(),
                        const SizedBox(width: 10),
                        const Text(
                          'Sign in with Google',
                          style: TextStyle(
                            fontFamily: 'DMSans',
                            fontSize: 15,
                            fontWeight: FontWeight.w600,
                            color: AppColors.textPrimary,
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

// ─────────────────────────── Shared Widgets ──────────────────────────────

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

class _FieldLabel extends StatelessWidget {
  const _FieldLabel(this.text);
  final String text;

  @override
  Widget build(BuildContext context) {
    return Text(
      text,
      style: const TextStyle(
        fontFamily: 'DMSans',
        fontSize: 13,
        fontWeight: FontWeight.w500,
        color: AppColors.textSecondary,
      ),
    );
  }
}

class _CountryField extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(14),
      child: Container(
        height: 54,
        color: AppColors.backgroundGrey,
        child: IntrinsicHeight(
          child: Row(
            children: [
              // Green left accent bar
              Container(width: 3, color: AppColors.primaryGreen),

              const SizedBox(width: 12),

              // Flag + code + chevron
              Row(
                children: [
                  const Text('🇳🇬', style: TextStyle(fontSize: 20)),
                  const SizedBox(width: 6),
                  const Text(
                    '+234',
                    style: TextStyle(
                      fontFamily: 'DMSans',
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(width: 4),
                  Icon(
                    Icons.expand_more_rounded,
                    size: 18,
                    color: AppColors.textSecondary,
                  ),
                ],
              ),

              // Vertical divider
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
                child: VerticalDivider(
                  color: AppColors.borderLight,
                  thickness: 1,
                  width: 1,
                ),
              ),

              // Country name
              Text(
                'Nigeria',
                style: TextStyle(
                  fontFamily: 'DMSans',
                  fontSize: 15,
                  color: AppColors.textSecondary.withOpacity(0.8),
                ),
              ),
            ],
          ),
        ),
      ),
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

/// Coloured Google "G" logo using RichText
class _GoogleLogo extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      width: 22,
      height: 22,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(color: AppColors.borderLight, width: 1),
      ),
      child: ClipOval(
        child: CustomPaint(
          painter: _GoogleGPainter(),
        ),
      ),
    );
  }
}

class _GoogleGPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final cx = size.width / 2;
    final cy = size.height / 2;
    final r = size.width * 0.44;

    // Blue arc
    canvas.drawArc(
      Rect.fromCircle(center: Offset(cx, cy), radius: r),
      -0.3,
      4.2,
      false,
      Paint()
        ..color = const Color(0xFF4285F4)
        ..strokeWidth = size.width * 0.18
        ..style = PaintingStyle.stroke
        ..strokeCap = StrokeCap.round,
    );

    // White fill cut for the G shape
    final wPaint = Paint()..color = Colors.white;
    canvas.drawRect(
      Rect.fromLTWH(cx - 0.5, cy - 2, size.width * 0.5, 4),
      wPaint,
    );

    // Green bottom arc
    canvas.drawArc(
      Rect.fromCircle(center: Offset(cx, cy), radius: r),
      0.1,
      1.4,
      false,
      Paint()
        ..color = const Color(0xFF34A853)
        ..strokeWidth = size.width * 0.18
        ..style = PaintingStyle.stroke
        ..strokeCap = StrokeCap.round,
    );

    // Red top-left arc
    canvas.drawArc(
      Rect.fromCircle(center: Offset(cx, cy), radius: r),
      -2.4,
      1.1,
      false,
      Paint()
        ..color = const Color(0xFFEA4335)
        ..strokeWidth = size.width * 0.18
        ..style = PaintingStyle.stroke
        ..strokeCap = StrokeCap.round,
    );

    // Yellow bottom-left arc
    canvas.drawArc(
      Rect.fromCircle(center: Offset(cx, cy), radius: r),
      1.55,
      1.2,
      false,
      Paint()
        ..color = const Color(0xFFFBBC05)
        ..strokeWidth = size.width * 0.18
        ..style = PaintingStyle.stroke
        ..strokeCap = StrokeCap.round,
    );
  }

  @override
  bool shouldRepaint(_) => false;
}