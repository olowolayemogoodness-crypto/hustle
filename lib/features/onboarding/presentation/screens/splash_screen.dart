import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:hustle/core/router/routes.dart';
import 'package:hustle/core/supabase/supabase_config.dart';
import 'package:hustle/features/auth/presentation/providers/auth_provider.dart';
import 'package:supabase_flutter/supabase_flutter.dart';


class SplashScreen extends ConsumerStatefulWidget {
  const SplashScreen({super.key});

  @override
  ConsumerState<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends ConsumerState<SplashScreen>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  late final Animation<double> _fadeIn;
  late final Animation<double> _scaleIn;
  late final Animation<double> _slideUp;

  @override
  void initState() {
    super.initState();

    // Add this temporarily anywhere in your Flutter app
// e.g. in splash screen initState just to grab the token

// Add temporarily in splash screen or anywhere after login
// In Flutter, add this temporarily after login
// In Flutter — add this after login





    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1100),
    );

    _fadeIn = CurvedAnimation(
      parent: _controller,
      curve: const Interval(0.0, 0.6, curve: Curves.easeOut),
    );

    _scaleIn = Tween<double>(begin: 0.72, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.0, 0.65, curve: Curves.elasticOut),
      ),
    );

    _slideUp = Tween<double>(begin: 24.0, end: 0.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.3, 0.85, curve: Curves.easeOut),
      ),
    );

    _controller.forward();

    // Minimum splash duration to show animation
    Future.delayed(const Duration(milliseconds: 1400), () {
      if (!mounted) return;
      _navigateIfReady();
    });

    // Timeout after 3 seconds to prevent infinite loading
    Future.delayed(const Duration(seconds: 3), () {
      if (!mounted) return;
      _navigateIfReady(forceNavigate: true);
    });
  }

  void _navigateIfReady({bool forceNavigate = false}) {
    final auth = ref.read(authProvider);

    // If still loading and not forced, wait for next state change
    if ((auth is AuthInitial || auth is AuthLoading) && !forceNavigate) {
      ref.listenManual(authProvider, (previous, next) {
        // Stop listening once we get a non-loading state
        if (next is AuthInitial || next is AuthLoading) return;
        if (!mounted) return;
        _redirectFromState(next);
      });
      return;
    }

    // If forced navigation or resolved state, navigate now
    if (!mounted) return;
    _redirectFromState(auth);
  }

  void _redirectFromState(AppAuthState auth) {
    if (!mounted) return;

    if (auth is AuthAuthenticated) {
      auth.user.needsRole
          ? context.go(Routes.roleSelect)
          : context.go(Routes.discovery);
    } else if (auth is AuthUnauthenticated) {
      context.go(Routes.phoneAuth);
    } else {
      // Still in loading/error state after timeout, go to phone auth as fallback
      context.go(Routes.phoneAuth);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  // ── Brand colours ──────────────────────────────────────────────────────────
  static const Color _bgCenter = Color(0xFF0A5C38); // mid-green
  static const Color _bgEdge = Color(0xFF052E1C); // deep forest
  static const Color _gold = Color(0xFFCB9A2E); // amber/gold accent
  static const Color _logoWhite = Color(0xFFF5F5F5);

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.sizeOf(context);

    return Scaffold(
      backgroundColor: _bgEdge,
      body: Container(
        width: double.infinity,
        height: double.infinity,
        // Radial gradient: brighter centre, darker edges — matching the mockup
        decoration: const BoxDecoration(
          gradient: RadialGradient(
            center: Alignment(0.0, -0.15),
            radius: 1.05,
            colors: [_bgCenter, _bgEdge],
            stops: [0.0, 1.0],
          ),
        ),
        child: SafeArea(
          child: Stack(
            alignment: Alignment.center,
            children: [
              // ── Centre content ───────────────────────────────────────────
              AnimatedBuilder(
                animation: _controller,
                builder: (context, child) => FadeTransition(
                  opacity: _fadeIn,
                  child: Transform.translate(
                    offset: Offset(0, _slideUp.value),
                    child: child,
                  ),
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // Logo circle
                    AnimatedBuilder(
                      animation: _scaleIn,
                      builder: (_, child) =>
                          Transform.scale(scale: _scaleIn.value, child: child),
                      child: _LogoCircle(gold: _gold, logoWhite: _logoWhite),
                    ),

                    const SizedBox(height: 28),

                    // App name
                    Text(
                      'Hustle',
                      style: TextStyle(
                        fontFamily: 'Poppins', // swap to your font
                        fontSize: 38,
                        fontWeight: FontWeight.w800,
                        color: _logoWhite,
                        letterSpacing: 0.5,
                        height: 1.0,
                      ),
                    ),

                    const SizedBox(height: 10),

                    // Tagline
                    Text(
                      'Work Near You. Get Paid Securely.',
                      style: TextStyle(
                        fontFamily: 'Poppins',
                        fontSize: 13.5,
                        fontWeight: FontWeight.w400,
                        color: _logoWhite.withOpacity(0.72),
                        letterSpacing: 0.2,
                      ),
                    ),
                  ],
                ),
              ),

              // ── Gold bottom bar ──────────────────────────────────────────
              Positioned(
                bottom: size.height * 0.042,
                child: AnimatedBuilder(
                  animation: _fadeIn,
                  builder: (_, child) =>
                      FadeTransition(opacity: _fadeIn, child: child),
                  child: Container(
                    width: 100,
                    height: 3.5,
                    decoration: BoxDecoration(
                      color: _gold,
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ── Extracted logo widget ──────────────────────────────────────────────────
class _LogoCircle extends StatelessWidget {
  const _LogoCircle({required this.gold, required this.logoWhite});

  final Color gold;
  final Color logoWhite;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 100,
      height: 100,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: logoWhite,
        border: Border.all(color: gold, width: 3.0),
        boxShadow: [
          BoxShadow(
            color: gold.withOpacity(0.35),
            blurRadius: 22,
            spreadRadius: 2,
          ),
          BoxShadow(
            color: Colors.black.withOpacity(0.25),
            blurRadius: 16,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Center(
        child: _HustleLockIcon(
          size: 44,
          color: const Color(0xFF0A5C38),
        ),
      ),
    );
  }
}

// ── Custom lock/person icon (matches mockup glyph) ─────────────────────────
class _HustleLockIcon extends StatelessWidget {
  const _HustleLockIcon({required this.size, required this.color});

  final double size;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      size: Size(size, size),
      painter: _LockPersonPainter(color: color),
    );
  }
}

class _LockPersonPainter extends CustomPainter {
  _LockPersonPainter({required this.color});
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.fill;

    final w = size.width;
    final h = size.height;

    // Head (circle)
    canvas.drawCircle(Offset(w * 0.5, h * 0.26), w * 0.155, paint);

    // Body / shoulders (rounded rect)
    final bodyRRect = RRect.fromRectAndRadius(
      Rect.fromCenter(
        center: Offset(w * 0.5, h * 0.50),
        width: w * 0.46,
        height: h * 0.22,
      ),
      Radius.circular(w * 0.12),
    );
    canvas.drawRRect(bodyRRect, paint);

    // Lock body (rounded rect)
    final lockRRect = RRect.fromRectAndRadius(
      Rect.fromCenter(
        center: Offset(w * 0.5, h * 0.72),
        width: w * 0.24,
        height: h * 0.24,
      ),
      Radius.circular(w * 0.06),
    );
    canvas.drawRRect(lockRRect, paint);

    // Lock keyhole (small circle)
    canvas.drawCircle(Offset(w * 0.5, h * 0.72), w * 0.05, paint);
  }

  @override
  bool shouldRepaint(_LockPersonPainter oldDelegate) => false;
}
