import 'dart:async';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hustle/core/network/dio_client.dart';
import '../../../../core/config/theme.dart';
import '../../../../core/utils/formatters.dart';
import '../providers/wallet_provider.dart';

class TopUpScreen extends ConsumerStatefulWidget {
  const TopUpScreen({super.key});

  @override
  ConsumerState<TopUpScreen> createState() => _TopUpScreenState();
}

class _TopUpScreenState extends ConsumerState<TopUpScreen> {

 void _showCreateVADialog() {
  showModalBottomSheet(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.white,
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
    ),
    builder: (_) => _CreateVASheet(
      onCreated: _generateVA, // ← auto-retry after creation
    ),
  );
}

  final _amountCtrl = TextEditingController();
  
  bool   _loading       = false;
  bool   _vaGenerated   = false;
  String? _vaNumber;
  String? _bankName;
  String? _accountName;
  String? _reference;
    int    _previousBalance  = 0;   // ← add this

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
// lib/features/wallet/presentation/screens/topup_screen.dart
// Update _generateVA()
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
    // Debug prints
    print('API URL: ${DioClient.instance.options.baseUrl}');
    final meResp = await DioClient.instance.get('/api/v1/auth/me');
    print('User: ${meResp.data}');

    final balanceResp = await DioClient.instance.get('/api/v1/wallet/balance');
    print('Balance: ${balanceResp.data}');
    _previousBalance = balanceResp.data['available_kobo'] as int? ?? 0;

    final response = await DioClient.instance.get('/api/v1/wallet/virtual-account');
    print('VA: ${response.data}');

    setState(() {
      _vaNumber    = response.data['virtual_account_number'];
      _bankName    = response.data['bank_name'] ?? 'GTBank';
      _accountName = 'Hustle Platform';
      _amountKobo  = naira * 100;
      _vaGenerated = true;
    });

    _startPolling();

  } on DioException catch (e) {
    print('Error: ${e.response?.statusCode} ${e.response?.data}');
    if (e.response?.statusCode == 404) {
      _showCreateVADialog();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: ${e.response?.data ?? e.message}')),
      );
    }
  } finally {
    if (mounted) setState(() => _loading = false);
  }
}

void _startPolling() {
  _pollTimer = Timer.periodic(const Duration(seconds: 5), (_) async {
    if (!mounted) return;
    try {
      final balance = await DioClient.instance.get('/api/v1/wallet/balance');
      final available = balance.data['available_kobo'] as int? ?? 0;
      if (available > _previousBalance) {
        _pollTimer?.cancel();
        _countdownTimer?.cancel();
        ref.invalidate(walletProvider);
        if (mounted) _showSuccess();
      }
    } catch (_) {}
  });
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
    required this.onNewTransfer,
  });

  final String    vaNumber, bankName, accountName;
  final int       amountKobo;
  final VoidCallback onNewTransfer;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Info banner
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            color: AppColors.primaryGreenLight,
            borderRadius: BorderRadius.circular(10),
          ),
          child: Row(
            children: const [
              Icon(Icons.info_outline_rounded,
                  size: 16, color: AppColors.primaryGreen),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  'This account is permanent. Transfer anytime to top up.',
                  style: TextStyle(
                    fontFamily: 'DMSans',
                    fontSize: 13,
                    color: AppColors.primaryGreen,
                    height: 1.4,
                  ),
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 24),

        const Text(
          'Transfer to this account',
          style: TextStyle(
            fontFamily: 'DMSans',
            fontSize: 14,
            color: AppColors.textSecondary,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          Formatters.naira(amountKobo),
          style: const TextStyle(
            fontFamily: 'Syne',
            fontSize: 36,
            fontWeight: FontWeight.w800,
            color: AppColors.primaryGreen,
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
                color: Colors.black.withOpacity(0.05),
                blurRadius: 10,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Column(
            children: [
              _DetailRow(label: 'Bank', value: bankName),
              const Divider(height: 24),
              _DetailRow(
                label: 'Account Number',
                value: vaNumber,
                copyable: true,
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

        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: const Color(0xFFFEF3C7),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: const [
              Icon(Icons.warning_amber_rounded,
                  size: 16, color: Color(0xFFF59E0B)),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Transfer the EXACT amount shown. '
                  'Different amounts will be automatically refunded by Squad.',
                  style: TextStyle(
                    fontFamily: 'DMSans',
                    fontSize: 12.5,
                    color: Color(0xFF92400E),
                    height: 1.5,
                  ),
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 20),

        SizedBox(
          width: double.infinity,
          height: 52,
          child: OutlinedButton(
            onPressed: onNewTransfer,
            style: OutlinedButton.styleFrom(
              side: const BorderSide(color: AppColors.primaryGreen),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14),
              ),
            ),
            child: const Text(
              'Change Amount',
              style: TextStyle(
                fontFamily: 'DMSans',
                fontSize: 15,
                fontWeight: FontWeight.w600,
                color: AppColors.primaryGreen,
              ),
            ),
          ),
        ),
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
// Update _CreateVASheet to accept callback
class _CreateVASheet extends StatefulWidget {
  const _CreateVASheet({this.onCreated});
  final VoidCallback? onCreated;  // ← add this

  @override
  State<_CreateVASheet> createState() => _CreateVASheetState();
}

class _CreateVASheetState extends State<_CreateVASheet> {
  // In _CreateVASheetState — initialize with test values
final _firstNameCtrl   = TextEditingController(text: 'Test');
final _lastNameCtrl    = TextEditingController(text: 'User');
final _phoneCtrl       = TextEditingController(text: '08012345678');
final _bvnCtrl         = TextEditingController(text: '22222222222');
final _dobCtrl         = TextEditingController(text: '01/01/1990');
final _addressCtrl     = TextEditingController(text: '22 Lagos Street');
final _beneficiaryCtrl = TextEditingController(text: '0000000000');
  String _gender             = '1';
  bool   _loading            = false;

Future<void> _submit() async {
  setState(() => _loading = true);
  try {
    await DioClient.instance.post(
      '/api/v1/wallet/virtual-account',
      data: {
        'first_name':          _firstNameCtrl.text.trim(),
        'last_name':           _lastNameCtrl.text.trim(),
        'phone':               _phoneCtrl.text.trim(),
        'bvn':                 _bvnCtrl.text.trim(),
        'dob':                 _dobCtrl.text.trim(),
        'gender':              _gender,
        'address':             _addressCtrl.text.trim(),
        'beneficiary_account': _beneficiaryCtrl.text.trim(),
      },
    );

    if (mounted) {
      Navigator.pop(context); // close sheet
      // Retry generating VA after creation
      Future.delayed(const Duration(milliseconds: 500), () {
     if (mounted) {
  Navigator.pop(context);
  widget.onCreated?.call(); // ← call this
}
      });
    }

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

  @override
  void dispose() {
    _firstNameCtrl.dispose();
    _lastNameCtrl.dispose();
    _phoneCtrl.dispose();
    _bvnCtrl.dispose();
    _dobCtrl.dispose();
    _addressCtrl.dispose();
    _beneficiaryCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.fromLTRB(
        24, 20, 24,
        MediaQuery.of(context).viewInsets.bottom + 24,
      ),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Set Up Your Wallet',
              style: TextStyle(
                fontFamily: 'Syne',
                fontSize: 20,
                fontWeight: FontWeight.w700,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 4),
            const Text(
              'Required once to receive payments',
              style: TextStyle(
                fontFamily: 'DMSans',
                fontSize: 13,
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 20),
            _Field('First Name',        _firstNameCtrl),
            _Field('Last Name',         _lastNameCtrl),
            _Field('Phone (080...)',     _phoneCtrl, type: TextInputType.phone),
            _Field('BVN (11 digits)',    _bvnCtrl,   type: TextInputType.number),
            _Field('DOB (MM/DD/YYYY)',  _dobCtrl),
            _Field('Address',           _addressCtrl),
            _Field('GTBank Account No', _beneficiaryCtrl, type: TextInputType.number),
            const SizedBox(height: 8),
            // Gender selector
            Row(
              children: [
                const Text('Gender: ', style: TextStyle(fontFamily: 'DMSans')),
                const SizedBox(width: 12),
                _GenderChip('Male',   '1', _gender, (v) => setState(() => _gender = v)),
                const SizedBox(width: 8),
                _GenderChip('Female', '2', _gender, (v) => setState(() => _gender = v)),
              ],
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: _loading ? null : _submit,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primaryGreen,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: _loading
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text(
                        'Create Virtual Account',
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
}

class _Field extends StatelessWidget {
  const _Field(this.label, this.ctrl, {this.type = TextInputType.text});
  final String                label;
  final TextEditingController ctrl;
  final TextInputType          type;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: TextField(
        controller:   ctrl,
        keyboardType: type,
        decoration: InputDecoration(
          labelText:  label,
          filled:     true,
          fillColor:  AppColors.backgroundGrey,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10),
            borderSide:   BorderSide.none,
          ),
        ),
      ),
    );
  }
}

class _GenderChip extends StatelessWidget {
  const _GenderChip(this.label, this.value, this.selected, this.onTap);
  final String   label, value, selected;
  final void Function(String) onTap;

  @override
  Widget build(BuildContext context) {
    final isActive = selected == value;
    return GestureDetector(
      onTap: () => onTap(value),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: isActive ? AppColors.primaryGreen : AppColors.backgroundGrey,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontFamily: 'DMSans',
            fontWeight: FontWeight.w600,
            color: isActive ? Colors.white : AppColors.textPrimary,
          ),
        ),
      ),
    );
  }
}