import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/config/theme.dart';
import '../providers/auth_provider.dart';
// for _CircleBackButton + _GlowButton
import 'package:hustle/features/auth/presentation/screens/phone_auth_screen.dart';
class OtpScreen extends ConsumerStatefulWidget {
  const OtpScreen({super.key, required this.phone});
  final String phone;

  @override
  ConsumerState<OtpScreen> createState() => _OtpScreenState();
}

class _OtpScreenState extends ConsumerState<OtpScreen> {
  final List<TextEditingController> _ctrls =
      List.generate(6, (_) => TextEditingController());
  final List<FocusNode> _nodes = List.generate(6, (_) => FocusNode());

  int _secondsLeft = 600; // 10 minutes
  Timer? _timer;
  bool _loading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _startTimer();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _nodes[0].requestFocus();
    });
    for (var i = 0; i < 6; i++) {
      _nodes[i].addListener(() => setState(() {}));
    }
  }

  void _startTimer() {
    _timer?.cancel();
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (!mounted) return;
      setState(() {
        if (_secondsLeft > 0) _secondsLeft--;
      });
    });
  }

  /// Formats as "0:45" or "1:30" (never pads minutes)
  String get _timerDisplay {
    final m = _secondsLeft ~/ 60;
    final s = _secondsLeft % 60;
    return '$m:${s.toString().padLeft(2, '0')}';
  }

  String get _maskedPhone {
    final p = widget.phone;
    if (p.startsWith('+234') && p.length >= 7) {
      final local = p.substring(4); // 8031234567
      if (local.length >= 3) {
        return '+234 ${local.substring(0, 3)} *** ***';
      }
    }
    return p;
  }

  String get _otp => _ctrls.map((c) => c.text).join();

  void _onChanged(int index, String value) {
    // Handle paste of full OTP
    if (value.length > 1) {
      final digits = value.replaceAll(RegExp(r'\D'), '');
      for (var i = 0; i < 6 && i < digits.length; i++) {
        _ctrls[i].text = digits[i];
      }
      _nodes[5].requestFocus();
      setState(() {});
      if (_otp.length == 6) _submit();
      return;
    }

    setState(() {});

    if (value.isNotEmpty && index < 5) {
      _nodes[index + 1].requestFocus();
    } else if (value.isEmpty && index > 0) {
      _nodes[index - 1].requestFocus();
    }

    if (_otp.length == 6) _submit();
  }

  void _onBackspace(int index) {
    if (_ctrls[index].text.isEmpty && index > 0) {
      _ctrls[index - 1].clear();
      _nodes[index - 1].requestFocus();
      setState(() {});
    }
  }

  Future<void> _submit() async {
    if (_otp.length != 6 || _loading) return;
    setState(() { _loading = true; _error = null; });

    final ok = await ref
        .read(authProvider.notifier)
        .verifyOtp(widget.phone, _otp);

    if (!ok && mounted) {
      setState(() {
        _loading = false;
        _error = 'Incorrect code. Please try again.';
      });
      for (final c in _ctrls) c.clear();
      _nodes[0].requestFocus();
    }
    // On success GoRouter redirect handles navigation
  }

  Future<void> _resend() async {
    if (_secondsLeft > 0) return;
    setState(() {
      _secondsLeft = 600;
      _error = null;
    });
    for (final c in _ctrls) c.clear();
    _nodes[0].requestFocus();
    _startTimer();
    await ref.read(authProvider.notifier).sendOtp(widget.phone);
  }

  @override
  void dispose() {
    _timer?.cancel();
    for (final c in _ctrls) c.dispose();
    for (final n in _nodes) n.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Stack(
          children: [
            // ── Main scrollable content ───────────────────────────
            SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 16),

                  // Back button
                  CircleBackButton(),

                  const SizedBox(height: 32),

                  // ── Lock icon with badge ────────────────────────
                  Center(child: _LockIconWithBadge()),

                  const SizedBox(height: 28),

                  // ── Title ──────────────────────────────────────
                  const Center(
                    child: Text(
                      'Verify Your Number',
                      style: TextStyle(
                        fontFamily: 'Syne',
                        fontSize: 26,
                        fontWeight: FontWeight.w800,
                        color: AppColors.textPrimary,
                      ),
                    ),
                  ),
                  const SizedBox(height: 10),

                  // ── Subtitle with masked phone ──────────────────
                  Center(
                    child: RichText(
                      textAlign: TextAlign.center,
                      text: TextSpan(
                        style: const TextStyle(
                          fontFamily: 'DMSans',
                          fontSize: 14,
                          color: AppColors.textSecondary,
                          height: 1.5,
                        ),
                        children: [
                          const TextSpan(text: 'We sent a 6-digit code to '),
                          TextSpan(
                            text: _maskedPhone,
                            style: const TextStyle(
                              fontWeight: FontWeight.w700,
                              color: AppColors.textPrimary,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 36),

                  // ── OTP Boxes ───────────────────────────────────
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: List.generate(
                      6,
                      (i) => _OtpBox(
                        controller: _ctrls[i],
                        focusNode: _nodes[i],
                        onChanged: (v) => _onChanged(i, v),
                        onBackspace: () => _onBackspace(i),
                        hasError: _error != null,
                      ),
                    ),
                  ),

                  if (_error != null) ...[
                    const SizedBox(height: 10),
                    Text(
                      _error!,
                      style: const TextStyle(
                        fontFamily: 'DMSans',
                        fontSize: 13,
                        color: AppColors.accentRed,
                      ),
                    ),
                  ],

                  const SizedBox(height: 22),

                  // ── Timer row ────────────────────────────────────
                  if (_secondsLeft > 0) ...[
                    Center(
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.access_time_rounded,
                            size: 15,
                            color: const Color(0xFFF59E0B),
                          ),
                          const SizedBox(width: 5),
                          Text(
                            'Resend code in $_timerDisplay',
                            style: const TextStyle(
                              fontFamily: 'DMSans',
                              fontSize: 13.5,
                              fontWeight: FontWeight.w600,
                              color: Color(0xFFF59E0B),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 8),
                  ],

                  // ── Resend row ────────────────────────────────────
                  Center(
                    child: RichText(
                      text: TextSpan(
                        style: const TextStyle(
                          fontFamily: 'DMSans',
                          fontSize: 13.5,
                          color: AppColors.textSecondary,
                        ),
                        children: [
                          const TextSpan(text: "Didn't receive code? "),
                          WidgetSpan(
                            child: GestureDetector(
                              onTap: _secondsLeft == 0 ? _resend : null,
                              child: Text(
                                'Resend',
                                style: TextStyle(
                                  fontFamily: 'DMSans',
                                  fontSize: 13.5,
                                  fontWeight: FontWeight.w700,
                                  color: _secondsLeft == 0
                                      ? AppColors.primaryGreen
                                      : AppColors.textSecondary,
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 32),

                  // ── Verify button ─────────────────────────────────
                  GlowButton(
                    onPressed: (_loading || _otp.length != 6) ? null : _submit,
                    loading: _loading,
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: const [
                        Icon(Icons.shield_outlined,
                            color: Colors.white, size: 18),
                        SizedBox(width: 8),
                        Text(
                          'Verify',
                          style: TextStyle(
                            fontFamily: 'DMSans',
                            fontSize: 16,
                            fontWeight: FontWeight.w700,
                            color: Colors.white,
                          ),
                        ),
                      ],
                    ),
                  ),

                  // Spacer for bottom notice
                  const SizedBox(height: 120),
                ],
              ),
            ),

            // ── Security notice pinned to bottom ─────────────────
            Positioned(
              bottom: 16,
              left: 24,
              right: 24,
              child: _SecurityNotice(),
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────── Lock icon ────────────────────────────────────

class _LockIconWithBadge extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Stack(
      clipBehavior: Clip.none,
      children: [
        // Mint green rounded square
        Container(
          width: 72,
          height: 72,
          decoration: BoxDecoration(
            color: const Color(0xFFEDF8F1),
            borderRadius: BorderRadius.circular(20),
          ),
          child: const Center(
            child: Icon(
              Icons.lock_outline_rounded,
              color: AppColors.primaryGreen,
              size: 34,
            ),
          ),
        ),

        // Orange verified badge — top-right
        Positioned(
          top: -4,
          right: -4,
          child: Container(
            width: 24,
            height: 24,
            decoration: const BoxDecoration(
              color: Color(0xFFF59E0B),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.check_rounded,
              color: Colors.white,
              size: 14,
            ),
          ),
        ),
      ],
    );
  }
}

// ─────────────────────────── OTP Box ──────────────────────────────────────

class _OtpBox extends StatelessWidget {
  const _OtpBox({
    required this.controller,
    required this.focusNode,
    required this.onChanged,
    required this.onBackspace,
    this.hasError = false,
  });

  final TextEditingController controller;
  final FocusNode focusNode;
  final ValueChanged<String> onChanged;
  final VoidCallback onBackspace;
  final bool hasError;

  bool get _hasValue => controller.text.isNotEmpty;
  bool get _isFocused => focusNode.hasFocus;

  @override
  Widget build(BuildContext context) {
    final showGreenBorder = _hasValue || _isFocused;

    return SizedBox(
      width: 48,
      height: 56,
      child: RawKeyboardListener(
        focusNode: FocusNode(),
        onKey: (event) {
          if (event.logicalKey.keyLabel == 'Backspace') {
            onBackspace();
          }
        },
        child: TextFormField(
          controller: controller,
          focusNode: focusNode,
          keyboardType: TextInputType.number,
          textAlign: TextAlign.center,
          maxLength: 1,
          onChanged: onChanged,
          style: TextStyle(
            fontFamily: 'Syne',
            fontSize: 22,
            fontWeight: FontWeight.w800,
            color: hasError ? AppColors.accentRed : AppColors.textPrimary,
          ),
          decoration: InputDecoration(
            counterText: '',
            filled: true,
            fillColor: showGreenBorder && !hasError
                ? Colors.white
                : hasError
                    ? AppColors.accentRed.withOpacity(0.06)
                    : const Color(0xFFF2F4F5),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: _hasValue && !hasError
                  ? const BorderSide(
                      color: AppColors.primaryGreen, width: 2)
                  : BorderSide.none,
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(
                color: hasError
                    ? AppColors.accentRed
                    : AppColors.primaryGreen,
                width: 2,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────── Security Notice ──────────────────────────────

class _SecurityNotice extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        color: const Color(0xFFEDF8F1),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Padding(
            padding: EdgeInsets.only(top: 1),
            child: Icon(
              Icons.info_outline_rounded,
              size: 16,
              color: AppColors.primaryGreen,
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: RichText(
              text: const TextSpan(
                style: TextStyle(
                  fontFamily: 'DMSans',
                  fontSize: 12.5,
                  color: AppColors.textSecondary,
                  height: 1.5,
                ),
                children: [
                  TextSpan(text: 'For your security, this code expires in '),
                  TextSpan(
                    text: '10 minutes',
                    style: TextStyle(
                      fontWeight: FontWeight.w700,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  TextSpan(text: '. Never share it with anyone.'),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}