// lib/features/wallet/presentation/screens/withdrawal_screen.dart
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hustle/core/network/dio_client.dart';
import '../../../../core/config/theme.dart';
import '../../../../core/utils/formatters.dart';
import '../providers/wallet_provider.dart';

// ── Bank list ─────────────────────────────────────────────────────
const _kBanks = [
  ('Access Bank',    '044'),
  ('GTBank',         '058'),
  ('Zenith Bank',    '057'),
  ('First Bank',     '011'),
  ('UBA',            '033'),
  ('Fidelity Bank',  '070'),
  ('FCMB',           '214'),
  ('Stanbic IBTC',   '221'),
  ('Sterling Bank',  '232'),
  ('Union Bank',     '032'),
  ('Wema Bank',      '035'),
  ('Kuda MFB',       '50211'),
  ('OPay',           '100004'),
  ('PalmPay',        '100033'),
  ('Moniepoint',     '50515'),
];

class WithdrawalScreen extends ConsumerStatefulWidget {
  const WithdrawalScreen({super.key});

  @override
  ConsumerState<WithdrawalScreen> createState() => _WithdrawalScreenState();
}

class _WithdrawalScreenState extends ConsumerState<WithdrawalScreen> {
  final _amountCtrl  = TextEditingController();
  final _accountCtrl = TextEditingController();

  String? _selectedBankCode;
  String? _selectedBankName;
  String? _accountName;       // returned from lookup
  bool    _lookingUp  = false;
  bool    _submitting = false;
  String? _error;

  // ── Lookup account name ───────────────────────────────────────

  Future<void> _lookupAccount() async {
    final account = _accountCtrl.text.trim();
    if (_selectedBankCode == null || account.length != 10) return;

    setState(() { _lookingUp = true; _accountName = null; _error = null; });

    try {
      final response = await DioClient.instance.post(
        '/api/v1/wallet/lookup',
        data: {
          'bank_code':      _selectedBankCode,
          'account_number': account,
        },
      );
      setState(() {
        _accountName = response.data['account_name'] as String?;
      });
    } on DioException catch (e) {
      setState(() {
        _error = e.response?.data['detail'] ?? 'Account lookup failed';
      });
    } finally {
      if (mounted) setState(() => _lookingUp = false);
    }
  }

  // ── Submit withdrawal ─────────────────────────────────────────

  Future<void> _withdraw() async {
    final naira = int.tryParse(
      _amountCtrl.text.replaceAll(',', ''),
    ) ?? 0;

    if (naira < 100) {
      setState(() => _error = 'Minimum withdrawal is ₦100');
      return;
    }
    if (_selectedBankCode == null) {
      setState(() => _error = 'Select a bank');
      return;
    }
    if (_accountCtrl.text.trim().length != 10) {
      setState(() => _error = 'Enter a valid 10-digit account number');
      return;
    }
    if (_accountName == null) {
      setState(() => _error = 'Verify account first');
      return;
    }

    setState(() { _submitting = true; _error = null; });

    try {
      await DioClient.instance.post(
        '/api/v1/wallet/withdraw',
        data: {
          'amount_kobo':    naira * 100,
          'bank_code':      _selectedBankCode,
          'account_number': _accountCtrl.text.trim(),
          'account_name':   _accountName,
        },
      );

      // Refresh wallet balance
      ref.invalidate(walletProvider);

      if (mounted) _showSuccess(naira);

    } on DioException catch (e) {
      setState(() {
        _error = e.response?.data['detail'] ?? 'Withdrawal failed';
      });
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  void _showSuccess(int naira) {
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
              'Withdrawal Initiated!',
              style: TextStyle(
                fontFamily: 'Syne',
                fontSize: 18,
                fontWeight: FontWeight.w700,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '${Formatters.naira(naira * 100)} is on its way to $_accountName.',
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontFamily: 'DMSans',
                fontSize: 14,
                color: AppColors.textSecondary,
                height: 1.5,
              ),
            ),
            const SizedBox(height: 6),
            const Text(
              'Usually arrives within minutes.',
              style: TextStyle(
                fontFamily: 'DMSans',
                fontSize: 13,
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  Navigator.pop(context); // close dialog
                  Navigator.pop(context); // close screen
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

  @override
  void dispose() {
    _amountCtrl.dispose();
    _accountCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final walletAsync = ref.watch(walletProvider);
    final availableKobo = walletAsync.whenOrNull(
      data: (w) => w.balance.available,
    ) ?? 0;

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        centerTitle: true,
        title: const Text(
          'Withdraw',
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
        padding: const EdgeInsets.symmetric(horizontal: 24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 8),

            // ── Available balance ──────────────────────────────
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.primaryGreenLight,
                borderRadius: BorderRadius.circular(14),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Available Balance',
                    style: TextStyle(
                      fontFamily: 'DMSans',
                      fontSize: 13,
                      color: AppColors.primaryGreen,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    Formatters.naira(availableKobo),
                    style: const TextStyle(
                      fontFamily: 'Syne',
                      fontSize: 26,
                      fontWeight: FontWeight.w800,
                      color: AppColors.primaryGreen,
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // ── Amount ────────────────────────────────────────
            const _Label('Amount'),
            const SizedBox(height: 8),
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
                      fontSize: 22,
                      fontWeight: FontWeight.w700,
                      color: AppColors.primaryGreen,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: TextField(
                      controller:   _amountCtrl,
                      keyboardType: TextInputType.number,
                      style: const TextStyle(
                        fontFamily: 'Syne',
                        fontSize: 22,
                        fontWeight: FontWeight.w700,
                        color: AppColors.textPrimary,
                      ),
                      decoration: const InputDecoration(
                        hintText:       '0',
                        hintStyle:      TextStyle(color: AppColors.textHint),
                        border:         InputBorder.none,
                        isDense:        true,
                        contentPadding: EdgeInsets.symmetric(vertical: 14),
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // Quick amounts
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              children: [1000, 5000, 10000, 20000].map((a) {
                return GestureDetector(
                  onTap: () => _amountCtrl.text = a.toString(),
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12, vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: AppColors.primaryGreenLight,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Text(
                      '₦${a >= 1000 ? '${a ~/ 1000}k' : a}',
                      style: const TextStyle(
                        fontFamily: 'DMSans',
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: AppColors.primaryGreen,
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),

            const SizedBox(height: 24),

            // ── Bank selector ─────────────────────────────────
            const _Label('Bank'),
            const SizedBox(height: 8),
            Container(
              decoration: BoxDecoration(
                color: AppColors.backgroundGrey,
                borderRadius: BorderRadius.circular(14),
              ),
              child: DropdownButtonFormField<String>(
                value: _selectedBankCode,
                decoration: const InputDecoration(
                  contentPadding: EdgeInsets.symmetric(
                    horizontal: 16, vertical: 14,
                  ),
                  border: InputBorder.none,
                ),
                hint: const Text(
                  'Select bank',
                  style: TextStyle(
                    fontFamily: 'DMSans',
                    color: AppColors.textHint,
                  ),
                ),
                items: _kBanks.map((bank) {
                  return DropdownMenuItem(
                    value: bank.$2,
                    child: Text(
                      bank.$1,
                      style: const TextStyle(
                        fontFamily: 'DMSans',
                        fontSize: 14,
                        color: AppColors.textPrimary,
                      ),
                    ),
                  );
                }).toList(),
                onChanged: (code) {
                  setState(() {
                    _selectedBankCode = code;
                    _selectedBankName = _kBanks
                        .firstWhere((b) => b.$2 == code).$1;
                    _accountName = null;
                  });
                  // Auto-lookup if account already entered
                  if (_accountCtrl.text.trim().length == 10) {
                    _lookupAccount();
                  }
                },
              ),
            ),

            const SizedBox(height: 16),

            // ── Account number ────────────────────────────────
            const _Label('Account Number'),
            const SizedBox(height: 8),
            Container(
              decoration: BoxDecoration(
                color: AppColors.backgroundGrey,
                borderRadius: BorderRadius.circular(14),
              ),
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller:   _accountCtrl,
                      keyboardType: TextInputType.number,
                      maxLength:    10,
                      onChanged:    (v) {
                        setState(() => _accountName = null);
                        if (v.length == 10) _lookupAccount();
                      },
                      decoration: const InputDecoration(
                        hintText:       '0000000000',
                        hintStyle:      TextStyle(color: AppColors.textHint),
                        border:         InputBorder.none,
                        counterText:    '',
                        contentPadding: EdgeInsets.symmetric(vertical: 14),
                      ),
                      style: const TextStyle(
                        fontFamily: 'DMSans',
                        fontSize: 15,
                        letterSpacing: 1,
                        color: AppColors.textPrimary,
                      ),
                    ),
                  ),
                  if (_lookingUp)
                    const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: AppColors.primaryGreen,
                      ),
                    ),
                ],
              ),
            ),

            // ── Account name (verified) ───────────────────────
            if (_accountName != null) ...[
              const SizedBox(height: 10),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 14, vertical: 10,
                ),
                decoration: BoxDecoration(
                  color: AppColors.primaryGreenLight,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Row(
                  children: [
                    const Icon(
                      Icons.check_circle_rounded,
                      size: 16,
                      color: AppColors.primaryGreen,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      _accountName!,
                      style: const TextStyle(
                        fontFamily: 'DMSans',
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: AppColors.primaryGreen,
                      ),
                    ),
                  ],
                ),
              ),
            ],

            // ── Error ─────────────────────────────────────────
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

            const SizedBox(height: 32),

            // ── Withdraw button ───────────────────────────────
            Container(
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
                onPressed: (_submitting || _accountName == null)
                    ? null
                    : _withdraw,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primaryGreen,
                  disabledBackgroundColor:
                      AppColors.primaryGreen.withOpacity(0.5),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(30),
                  ),
                  elevation: 0,
                ),
                child: _submitting
                    ? const SizedBox(
                        width: 22,
                        height: 22,
                        child: CircularProgressIndicator(
                          strokeWidth: 2.5,
                          color: Colors.white,
                        ),
                      )
                    : const Text(
                        'Withdraw',
                        style: TextStyle(
                          fontFamily: 'DMSans',
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                        ),
                      ),
              ),
            ),

            const SizedBox(height: 12),

            // ── Disclaimer ────────────────────────────────────
            const Center(
              child: Text(
                'Transfers usually arrive within 5 minutes.',
                style: TextStyle(
                  fontFamily: 'DMSans',
                  fontSize: 12,
                  color: AppColors.textHint,
                ),
              ),
            ),

            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }
}

// ── Shared label widget ───────────────────────────────────────────

class _Label extends StatelessWidget {
  const _Label(this.text);
  final String text;

  @override
  Widget build(BuildContext context) {
    return Text(
      text,
      style: const TextStyle(
        fontFamily: 'DMSans',
        fontSize: 13,
        fontWeight: FontWeight.w600,
        color: AppColors.textSecondary,
      ),
    );
  }
}