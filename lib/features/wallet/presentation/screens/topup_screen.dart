import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/config/theme.dart';
import '../../../../core/utils/formatters.dart';
import '../providers/wallet_provider.dart';

class TopUpScreen extends ConsumerStatefulWidget {
  const TopUpScreen({super.key});

  @override
  ConsumerState<TopUpScreen> createState() => _TopUpScreenState();
}

class _TopUpScreenState extends ConsumerState<TopUpScreen> {
  final _amountCtrl = TextEditingController();
  
  bool   _loading       = false;
  bool   _vaGenerated   = false;
  String? _vaNumber;
  String? _bankName;
  String? _accountName;
  String? _reference;
  int    _amountKobo    = 0;
  int    _secondsLeft   = 600;
  Timer? _countdownTimer;
  Timer? _pollTimer;

  @override
  void dispose() {
    _countdownTimer?.cancel();
    _pollTimer?.cancel();
    _amountCtrl.dispose();
    super.dispose();
  }

  Future<void> _generateVA() async {
    final naira = int.tryParse(_amountCtrl.text.replaceAll(',', '')) ?? 0;
    if (naira < 1000) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Minimum top-up is ₦1,000')),
      );
      return;
    }

    setState(() => _loading = true);

    try {
      final repo   = ref.read(squadRepositoryProvider);
      final result = await repo.initiateTopUp(
        amountKobo: naira * 100,
        duration:   600,
      );

      setState(() {
        _vaNumber    = result['virtual_account_number'];
        _bankName    = result['bank_name'];
        _accountName = result['account_name'];
        _reference   = result['reference'];
        _amountKobo  = naira * 100;
        _vaGenerated = true;
        _secondsLeft = 600;
      });

      _startCountdown();
      _startPolling();

    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _startCountdown() {
    _countdownTimer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (!mounted) return;
      setState(() {
        if (_secondsLeft > 0) {
          _secondsLeft--;
        } else {
          _countdownTimer?.cancel();
          _pollTimer?.cancel();
        }
      });
    });
  }

  void _startPolling() {
    // Poll every 5 seconds to check if payment came in
    _pollTimer = Timer.periodic(const Duration(seconds: 5), (_) async {
      if (!mounted || _reference == null) return;
      try {
        final repo   = ref.read(squadRepositoryProvider);
        final status = await repo.checkTopUpStatus(_reference!);
        if (status['status'] == 'success') {
          _pollTimer?.cancel();
          _countdownTimer?.cancel();
          ref.invalidate(walletProvider);
          if (mounted) _showSuccess();
        }
      } catch (_) {}
    });
  }

  void _showSuccess() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 64,
              height: 64,
              decoration: const BoxDecoration(
                color: AppColors.primaryGreenLight,
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.check_rounded,
                color: AppColors.primaryGreen,
                size: 36,
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'Payment Received!',
              style: TextStyle(
                fontFamily: 'Syne',
                fontSize: 18,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '${Formatters.naira(_amountKobo)} has been added to your wallet.',
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontFamily: 'DMSans',
                fontSize: 14,
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  Navigator.pop(context);
                  Navigator.pop(context);
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primaryGreen,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text(
                  'Done',
                  style: TextStyle(
                    fontFamily: 'DMSans',
                    fontWeight: FontWeight.w700,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String get _timerDisplay {
    final m = _secondsLeft ~/ 60;
    final s = _secondsLeft % 60;
    return '$m:${s.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: const Text(
          'Top Up Wallet',
          style: TextStyle(
            fontFamily: 'DMSans',
            fontSize: 17,
            fontWeight: FontWeight.w700,
            color: AppColors.textPrimary,
          ),
        ),
        leading: const BackButton(color: AppColors.textPrimary),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: _vaGenerated
            ? _VADetailsView(
                vaNumber:    _vaNumber!,
                bankName:    _bankName!,
                accountName: _accountName!,
                amountKobo:  _amountKobo,
                timerDisplay: _timerDisplay,
                timerExpired: _secondsLeft == 0,
                onNewTransfer: () => setState(() {
                  _vaGenerated = false;
                  _amountCtrl.clear();
                }),
              )
            : _AmountInputView(
                controller: _amountCtrl,
                loading:    _loading,
                onContinue: _generateVA,
              ),
      ),
    );
  }
}

// ─────────────────────────── Amount Input ─────────────────────────

class _AmountInputView extends StatelessWidget {
  const _AmountInputView({
    required this.controller,
    required this.loading,
    required this.onContinue,
  });

  final TextEditingController controller;
  final bool                  loading;
  final VoidCallback          onContinue;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Enter Amount',
          style: TextStyle(
            fontFamily: 'Syne',
            fontSize: 22,
            fontWeight: FontWeight.w700,
            color: AppColors.textPrimary,
          ),
        ),
        const SizedBox(height: 6),
        const Text(
          'Minimum ₦1,000',
          style: TextStyle(
            fontFamily: 'DMSans',
            fontSize: 13,
            color: AppColors.textSecondary,
          ),
        ),
        const SizedBox(height: 28),

        // Amount field
        Container(
          decoration: BoxDecoration(
            color: AppColors.backgroundGrey,
            borderRadius: BorderRadius.circular(14),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
          child: Row(
            children: [
              const Text(
                '₦',
                style: TextStyle(
                  fontFamily: 'Syne',
                  fontSize: 24,
                  fontWeight: FontWeight.w700,
                  color: AppColors.primaryGreen,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: TextField(
                  controller:  controller,
                  keyboardType: TextInputType.number,
                  style: const TextStyle(
                    fontFamily: 'Syne',
                    fontSize: 24,
                    fontWeight: FontWeight.w700,
                    color: AppColors.textPrimary,
                  ),
                  decoration: const InputDecoration(
                    hintText:    '0',
                    hintStyle:   TextStyle(color: AppColors.textHint),
                    border:      InputBorder.none,
                    isDense:     true,
                    contentPadding: EdgeInsets.symmetric(vertical: 14),
                  ),
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // Quick amount chips
        Wrap(
          spacing: 8,
          children: [1000, 5000, 10000, 20000, 50000].map((amount) {
            return GestureDetector(
              onTap: () => controller.text = amount.toString(),
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 14, vertical: 8,
                ),
                decoration: BoxDecoration(
                  color:        AppColors.primaryGreenLight,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  '₦${amount >= 1000 ? '${amount ~/ 1000}k' : amount}',
                  style: const TextStyle(
                    fontFamily:  'DMSans',
                    fontSize:    13,
                    fontWeight:  FontWeight.w600,
                    color:       AppColors.primaryGreen,
                  ),
                ),
              ),
            );
          }).toList(),
        ),

        const SizedBox(height: 32),

        SizedBox(
          width:  double.infinity,
          height: 52,
          child: ElevatedButton(
            onPressed: loading ? null : onContinue,
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primaryGreen,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14),
              ),
              elevation: 0,
            ),
            child: loading
                ? const CircularProgressIndicator(color: Colors.white)
                : const Text(
                    'Generate Account',
                    style: TextStyle(
                      fontFamily:  'DMSans',
                      fontSize:    16,
                      fontWeight:  FontWeight.w700,
                      color:       Colors.white,
                    ),
                  ),
          ),
        ),
      ],
    );
  }
}

// ─────────────────────────── VA Details View ──────────────────────

class _VADetailsView extends StatelessWidget {
  const _VADetailsView({
    required this.vaNumber,
    required this.bankName,
    required this.accountName,
    required this.amountKobo,
    required this.timerDisplay,
    required this.timerExpired,
    required this.onNewTransfer,
  });

  final String vaNumber, bankName, accountName, timerDisplay;
  final int    amountKobo;
  final bool   timerExpired;
  final VoidCallback onNewTransfer;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Timer
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          decoration: BoxDecoration(
            color: timerExpired
                ? AppColors.accentRed.withOpacity(0.1)
                : const Color(0xFFFEF3C7),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.access_time_rounded,
                size:  16,
                color: timerExpired
                    ? AppColors.accentRed
                    : const Color(0xFFF59E0B),
              ),
              const SizedBox(width: 6),
              Text(
                timerExpired
                    ? 'Expired — generate a new transfer'
                    : 'Expires in $timerDisplay',
                style: TextStyle(
                  fontFamily:  'DMSans',
                  fontSize:    13,
                  fontWeight:  FontWeight.w600,
                  color: timerExpired
                      ? AppColors.accentRed
                      : const Color(0xFFF59E0B),
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 24),

        const Text(
          'Transfer exactly',
          style: TextStyle(
            fontFamily: 'DMSans',
            fontSize:   14,
            color:      AppColors.textSecondary,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          Formatters.naira(amountKobo),
          style: const TextStyle(
            fontFamily:  'Syne',
            fontSize:    36,
            fontWeight:  FontWeight.w800,
            color:       AppColors.primaryGreen,
          ),
        ),
        const SizedBox(height: 4),
        const Text(
          'to this account',
          style: TextStyle(
            fontFamily: 'DMSans',
            fontSize:   14,
            color:      AppColors.textSecondary,
          ),
        ),

        const SizedBox(height: 28),

        // Account details card
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppColors.borderLight),
            boxShadow: [
              BoxShadow(
                color:  Colors.black.withOpacity(0.05),
                blurRadius: 10,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Column(
            children: [
              _DetailRow(label: 'Bank',    value: bankName),
              const Divider(height: 24),
              _DetailRow(
                label:     'Account Number',
                value:     vaNumber,
                copyable:  true,
              ),
              const Divider(height: 24),
              _DetailRow(label: 'Account Name', value: accountName),
              const Divider(height: 24),
              _DetailRow(
                label: 'Amount',
                value: Formatters.naira(amountKobo),
                valueColor: AppColors.primaryGreen,
              ),
            ],
          ),
        ),

        const SizedBox(height: 20),

        // Warning
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: AppColors.primaryGreenLight,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: const [
              Icon(
                Icons.info_outline_rounded,
                size:  16,
                color: AppColors.primaryGreen,
              ),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Transfer the EXACT amount shown. Different amounts will be automatically refunded.',
                  style: TextStyle(
                    fontFamily: 'DMSans',
                    fontSize:   12.5,
                    color:      AppColors.primaryGreen,
                    height:     1.5,
                  ),
                ),
              ),
            ],
          ),
        ),

        if (timerExpired) ...[
          const SizedBox(height: 20),
          SizedBox(
            width:  double.infinity,
            height: 52,
            child: ElevatedButton(
              onPressed: onNewTransfer,
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primaryGreen,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
              ),
              child: const Text(
                'Generate New Transfer',
                style: TextStyle(
                  fontFamily:  'DMSans',
                  fontSize:    15,
                  fontWeight:  FontWeight.w700,
                  color:       Colors.white,
                ),
              ),
            ),
          ),
        ],
      ],
    );
  }
}

class _DetailRow extends StatelessWidget {
  const _DetailRow({
    required this.label,
    required this.value,
    this.copyable  = false,
    this.valueColor = AppColors.textPrimary,
  });

  final String label, value;
  final bool   copyable;
  final Color  valueColor;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontFamily: 'DMSans',
            fontSize:   13,
            color:      AppColors.textSecondary,
          ),
        ),
        Row(
          children: [
            Text(
              value,
              style: TextStyle(
                fontFamily: 'DMSans',
                fontSize:   14,
                fontWeight: FontWeight.w700,
                color:      valueColor,
              ),
            ),
            if (copyable) ...[
              const SizedBox(width: 8),
              GestureDetector(
                onTap: () {
                  Clipboard.setData(ClipboardData(text: value));
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Account number copied'),
                      duration: Duration(seconds: 2),
                    ),
                  );
                },
                child: const Icon(
                  Icons.copy_rounded,
                  size:  16,
                  color: AppColors.primaryGreen,
                ),
              ),
            ],
          ],
        ),
      ],
    );
  }
}