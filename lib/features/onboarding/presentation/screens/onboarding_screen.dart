import 'package:flutter/material.dart';

// ─────────────────────────────────────────────
//  DATA MODEL
// ─────────────────────────────────────────────
class _OnboardingPage {
  final String imagePath;
  final Color bgColor;
  final String title;
  final String description;

  const _OnboardingPage({
    required this.imagePath,
    required this.bgColor,
    required this.title,
    required this.description,
  });
}

// ─────────────────────────────────────────────
//  SCREEN
// ─────────────────────────────────────────────
class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen>
    with TickerProviderStateMixin {
  final PageController _pageController = PageController();
  int _currentPage = 0;

  // ── Replace imagePath values with your actual asset paths ──
  final List<_OnboardingPage> _pages = const [
    _OnboardingPage(
      imagePath: 'assets/images/onboarding_1.png', // map + worker illustration
      bgColor: Color(0xFFF2F4F3),
      title: 'Find Jobs Near You',
      description:
          'Browse hundreds of local gigs on a live map — plumbing, driving, delivery and more, right in your area.',
    ),
    _OnboardingPage(
      imagePath: 'assets/images/onboarding_2.png', // safe + coins illustration
      bgColor: Color(0xFFEEF4F0),
      title: 'Funds Secured\nBefore You Start',
      description:
          'Employers lock payment in escrow before work begins. You get paid — no disputes, no delays.',
    ),
    _OnboardingPage(
      imagePath: 'assets/images/onboarding_3.png', // star trophy illustration
      bgColor: Color(0xFFFBF8EE),
      title: 'Build Your Trust\nScore',
      description:
          'Every job completed boosts your reputation. High scores unlock better jobs and future financial access.',
    ),
  ];

  late final AnimationController _fadeController;
  late final Animation<double> _fadeAnim;

  @override
  void initState() {
    super.initState();
    _fadeController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 400),
    );
    _fadeAnim = CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeIn,
    );
    _fadeController.forward();
  }

  @override
  void dispose() {
    _pageController.dispose();
    _fadeController.dispose();
    super.dispose();
  }

  bool get _isLastPage => _currentPage == _pages.length - 1;

  void _next() {
    if (_isLastPage) {
      _getStarted();
    } else {
      _fadeController.reset();
      _pageController.nextPage(
        duration: const Duration(milliseconds: 400),
        curve: Curves.easeInOut,
      );
      _fadeController.forward();
    }
  }

  void _skip() {
    _getStarted();
  }

  void _getStarted() {
    // TODO: Navigate to sign-up / home
    // Navigator.of(context).pushReplacementNamed('/signup');
  }

  void _alreadyHaveAccount() {
    // TODO: Navigate to login
    // Navigator.of(context).pushReplacementNamed('/login');
  }

  @override
  Widget build(BuildContext context) {
    final page = _pages[_currentPage];

    return Scaffold(
      backgroundColor: page.bgColor,
      body: AnimatedContainer(
        duration: const Duration(milliseconds: 500),
        color: page.bgColor,
        child: SafeArea(
          child: Column(
            children: [
              // ── Skip button ──────────────────────────────────
              Align(
                alignment: Alignment.topRight,
                child: TextButton(
                  onPressed: _skip,
                  child: Text(
                    'Skip',
                    style: TextStyle(
                      color: Colors.black54,
                      fontSize: 15,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ),

              // ── Illustration ──────────────────────────────────
              Expanded(
                child: PageView.builder(
                  controller: _pageController,
                  itemCount: _pages.length,
                  onPageChanged: (index) {
                    setState(() => _currentPage = index);
                    _fadeController.reset();
                    _fadeController.forward();
                  },
                  itemBuilder: (context, index) {
                    return FadeTransition(
                      opacity: _fadeAnim,
                      child: Center(
                        child: Image.asset(
                          _pages[index].imagePath,
                          height: 260,
                          fit: BoxFit.contain,
                          // Placeholder while you add real assets:
                          errorBuilder: (_, __, ___) => Container(
                            height: 260,
                            width: 260,
                            decoration: BoxDecoration(
                              color: Colors.white24,
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Icon(
                              Icons.image_outlined,
                              size: 80,
                              color: Colors.black26,
                            ),
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),

              // ── Bottom card ───────────────────────────────────
              Container(
                width: double.infinity,
                padding: const EdgeInsets.fromLTRB(28, 32, 28, 32),
                decoration: const BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.vertical(top: Radius.circular(32)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Dots indicator
                    _DotsIndicator(
                      count: _pages.length,
                      current: _currentPage,
                    ),
                    const SizedBox(height: 20),

                    // Title
                    AnimatedSwitcher(
                      duration: const Duration(milliseconds: 300),
                      child: Text(
                        page.title,
                        key: ValueKey(page.title),
                        style: const TextStyle(
                          fontSize: 26,
                          fontWeight: FontWeight.w800,
                          color: Color(0xFF0D0D0D),
                          height: 1.2,
                        ),
                      ),
                    ),
                    const SizedBox(height: 12),

                    // Description
                    AnimatedSwitcher(
                      duration: const Duration(milliseconds: 300),
                      child: Text(
                        page.description,
                        key: ValueKey(page.description),
                        style: const TextStyle(
                          fontSize: 14.5,
                          color: Color(0xFF6B7280),
                          height: 1.6,
                        ),
                      ),
                    ),
                    const SizedBox(height: 28),

                    // Next / Get Started button
                    SizedBox(
                      width: double.infinity,
                      height: 54,
                      child: ElevatedButton(
                        onPressed: _next,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF1A6B3C),
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(14),
                          ),
                          elevation: 0,
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              _isLastPage ? 'Get Started' : 'Next',
                              style: const TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            if (!_isLastPage) ...[
                              const SizedBox(width: 8),
                              const Icon(Icons.arrow_forward, size: 18),
                            ],
                          ],
                        ),
                      ),
                    ),

                    // "I already have an account" — only on last page
                    if (_isLastPage) ...[
                      const SizedBox(height: 16),
                      Center(
                        child: GestureDetector(
                          onTap: _alreadyHaveAccount,
                          child: const Text(
                            'I already have an account',
                            style: TextStyle(
                              fontSize: 14,
                              color: Color(0xFF374151),
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────
//  DOTS INDICATOR WIDGET
// ─────────────────────────────────────────────
class _DotsIndicator extends StatelessWidget {
  final int count;
  final int current;

  const _DotsIndicator({required this.count, required this.current});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: List.generate(count, (i) {
        final isActive = i == current;
        return AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeInOut,
          margin: const EdgeInsets.only(right: 6),
          width: isActive ? 28 : 8,
          height: 8,
          decoration: BoxDecoration(
            color: isActive
                ? const Color(0xFF1A6B3C)
                : const Color(0xFFD1D5DB),
            borderRadius: BorderRadius.circular(4),
          ),
        );
      }),
    );
  }
}