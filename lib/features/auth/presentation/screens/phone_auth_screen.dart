import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hustle/core/supabase/supabase_config.dart';
import '../../../../core/config/theme.dart';
import '../providers/auth_provider.dart';

class PhoneAuthScreen extends ConsumerStatefulWidget {
  const PhoneAuthScreen({super.key});

  @override
  ConsumerState<PhoneAuthScreen> createState() => _PhoneAuthScreenState();
}

class _PhoneAuthScreenState extends ConsumerState<PhoneAuthScreen> {
  bool _loading = false;
  String? _error;

 Future<void> _signInWithGoogle() async {
  setState(() {
    _loading = true;
    _error = null;
  });

  final ok = await ref.read(authProvider.notifier).signInWithGoogle();

  if (!ok && mounted) {
    setState(() {
      _loading = false;
      _error = (ref.read(authProvider) as AuthError?)?.message;
    });
  }

  if (ok) {
    final session = SupabaseConfig.auth.currentSession;
    final token = session?.accessToken;

    print('Token available: ${token != null}');
  }
}

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 48),
              const Text(
                'Welcome to\nHustle',
                style: TextStyle(
                  fontFamily: 'Syne',
                  fontSize: 34,
                  fontWeight: FontWeight.w800,
                  color: AppColors.textPrimary,
                  height: 1.2,
                ),
              ),
              const SizedBox(height: 10),
              const Text(
                'Work near you. Get paid securely.',
                style: TextStyle(
                  fontFamily: 'DMSans',
                  fontSize: 15,
                  color: AppColors.textSecondary,
                ),
              ),
              const Spacer(),
              if (_error != null) ...[
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppColors.accentRed.withOpacity(0.08),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Text(
                    _error!,
                    style: const TextStyle(
                      fontFamily: 'DMSans',
                      fontSize: 13,
                      color: AppColors.accentRed,
                    ),
                  ),
                ),
                const SizedBox(height: 16),
              ],
              // Google button
              GlowButton(
                onPressed: _loading ? null : _signInWithGoogle,
                loading: _loading,
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}

class GlowButton extends StatelessWidget {
  const GlowButton({required this.onPressed, required this.loading});
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
            color: Colors.black.withOpacity(0.08),
            blurRadius: 16,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.white,
          foregroundColor: AppColors.textPrimary,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(30),
            side: const BorderSide(color: AppColors.borderLight),
          ),
        ),
        child: loading
            ? const SizedBox(
                width: 22,
                height: 22,
                child: CircularProgressIndicator(
                  strokeWidth: 2.5,
                  color: AppColors.primaryGreen,
                ),
              )
            : Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: const [
                  _GoogleLogo(),
                  SizedBox(width: 12),
                  Text(
                    'Sign in with Google',
                    style: TextStyle(
                      fontFamily: 'DMSans',
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
      ),
    );
  }
}
class _GoogleLogo extends StatelessWidget {
  const _GoogleLogo();

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
    final r  = size.width * 0.44;

    // Blue
    canvas.drawArc(
      Rect.fromCircle(center: Offset(cx, cy), radius: r),
      -0.3, 4.2, false,
      Paint()
        ..color = const Color(0xFF4285F4)
        ..strokeWidth = size.width * 0.18
        ..style = PaintingStyle.stroke
        ..strokeCap = StrokeCap.round,
    );

    // White cut
    canvas.drawRect(
      Rect.fromLTWH(cx - 0.5, cy - 2, size.width * 0.5, 4),
      Paint()..color = Colors.white,
    );

    // Green
    canvas.drawArc(
      Rect.fromCircle(center: Offset(cx, cy), radius: r),
      0.1, 1.4, false,
      Paint()
        ..color = const Color(0xFF34A853)
        ..strokeWidth = size.width * 0.18
        ..style = PaintingStyle.stroke
        ..strokeCap = StrokeCap.round,
    );

    // Red
    canvas.drawArc(
      Rect.fromCircle(center: Offset(cx, cy), radius: r),
      -2.4, 1.1, false,
      Paint()
        ..color = const Color(0xFFEA4335)
        ..strokeWidth = size.width * 0.18
        ..style = PaintingStyle.stroke
        ..strokeCap = StrokeCap.round,
    );

    // Yellow
    canvas.drawArc(
      Rect.fromCircle(center: Offset(cx, cy), radius: r),
      1.55, 1.2, false,
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