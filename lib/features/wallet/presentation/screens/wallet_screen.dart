import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:hustle/core/router/routes.dart';
import '../../../../core/config/theme.dart';
import '../../../../core/utils/formatters.dart';
import '../../data/models/wallet_model.dart';
import '../providers/wallet_provider.dart';

class WalletScreen extends ConsumerWidget {
  const WalletScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final walletAsync = ref.watch(walletProvider);

    return Scaffold(
      backgroundColor: AppColors.backgroundWhite,
      appBar: AppBar(
        backgroundColor: AppColors.backgroundWhite,
        elevation: 0,
        centerTitle: true,
        title: const Text(
          'Wallet',
          style: TextStyle(
            fontFamily: 'DMSans',
            fontSize: 18,
            fontWeight: FontWeight.w700,
            color: AppColors.textPrimary,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_outlined, color: AppColors.textPrimary),
            onPressed: () {},
          ),
        ],
      ),
      body: walletAsync.when(
        loading: () => const Center(
          child: CircularProgressIndicator(color: AppColors.primaryGreen),
        ),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (wallet) => RefreshIndicator(
          color: AppColors.primaryGreen,
          onRefresh: () => ref.read(walletProvider.notifier).refresh(),
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 8),
                _BalanceCard(balance: wallet.balance),
                const SizedBox(height: 16),
                _StatsRow(stats: wallet.stats),
                const SizedBox(height: 20),
                _EarningsChart(earnings: wallet.monthlyEarnings),
                const SizedBox(height: 20),
                _TransactionHistory(transactions: wallet.transactions),
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────── Balance Card ────────────────────────────

class _BalanceCard extends StatelessWidget {
  const _BalanceCard({required this.balance});
  final WalletBalance balance;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: AppColors.primaryGreen,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Available Balance',
            style: TextStyle(
              fontFamily: 'DMSans',
              fontSize: 13,
              fontWeight: FontWeight.w500,
              color: Colors.white70,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            Formatters.naira(balance.available),
            style: const TextStyle(
              fontFamily: 'Syne',
              fontSize: 34,
              fontWeight: FontWeight.w800,
              color: Colors.white,
              letterSpacing: -0.5,
            ),
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              _BalancePill(
                color: AppColors.accentYellow,
                label: 'Escrow Held: ${Formatters.naira(balance.locked)}',
              ),
              const SizedBox(width: 14),
              _BalancePill(
                color: AppColors.success,
                label: 'This Month: ${Formatters.naira(balance.thisMonth)}',
              ),
            ],
          ),
          const SizedBox(height: 18),
      Row(
  children: [
    Expanded(
      child: _CardButton(
        label: 'Withdraw',
        icon: Icons.arrow_upward_rounded,
        onTap: () => context.push(Routes.withdrawal), // ← add this
      ),
    ),
    const SizedBox(width: 12),
    Expanded(
      child: _CardButton(
        label: '+ Add Money',
        onTap: () => context.push(Routes.topUp), // ← add this
        filled: true,
      ),
    ),
  ],
),
        ],
      ),
    );
  }
}

class _BalancePill extends StatelessWidget {
  const _BalancePill({required this.color, required this.label});
  final Color color;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 5),
        Text(
          label,
          style: const TextStyle(
            fontFamily: 'DMSans',
            fontSize: 11.5,
            color: Colors.white,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }
}

class _CardButton extends StatelessWidget {
  const _CardButton({
    required this.label,
    this.icon,
    required this.onTap,
    this.filled = false,
  });
  final String label;
  final IconData? icon;
  final VoidCallback onTap;
  final bool filled;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: filled ? Colors.white.withOpacity(0.15) : Colors.transparent,
          borderRadius: BorderRadius.circular(30),
          border: Border.all(color: Colors.white, width: 1.5),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (icon != null) ...[
              Icon(icon, color: Colors.white, size: 15),
              const SizedBox(width: 6),
            ],
            Text(
              label,
              style: const TextStyle(
                fontFamily: 'DMSans',
                fontSize: 13.5,
                fontWeight: FontWeight.w600,
                color: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────── Stats Row ────────────────────────────

class _StatsRow extends StatelessWidget {
  const _StatsRow({required this.stats});
  final WorkerStats stats;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: _StatCard(
            icon: Icons.check_circle_outline_rounded,
            iconColor: AppColors.primaryGreen,
            value: '${stats.jobsDone}',
            label: 'Jobs Done',
            tag: 'Done',
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: _StatCard(
            icon: Icons.trending_up_rounded,
            iconColor: AppColors.primaryGreen,
            value: Formatters.nairaCompact(stats.avgPerJob),
            label: 'Avg / Job',
            tag: 'Avg',
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: _StatCard(
            icon: Icons.star_rounded,
            iconColor: AppColors.starColor,
            value: stats.rating.toStringAsFixed(1),
            label: 'Rating',
            tag: 'Top',
          ),
        ),
      ],
    );
  }
}

class _StatCard extends StatelessWidget {
  const _StatCard({
    required this.icon,
    required this.iconColor,
    required this.value,
    required this.label,
    required this.tag,
  });
  final IconData icon;
  final Color iconColor;
  final String value;
  final String label;
  final String tag;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppColors.borderLight),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 15, color: iconColor),
              const SizedBox(width: 4),
              Text(
                tag,
                style: TextStyle(
                  fontFamily: 'DMSans',
                  fontSize: 10.5,
                  fontWeight: FontWeight.w600,
                  color: iconColor,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            value,
            style: const TextStyle(
              fontFamily: 'Syne',
              fontSize: 20,
              fontWeight: FontWeight.w700,
              color: AppColors.textPrimary,
            ),
          ),
          Text(
            label,
            style: const TextStyle(
              fontFamily: 'DMSans',
              fontSize: 11,
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────── Earnings Chart ────────────────────────────

class _EarningsChart extends StatelessWidget {
  const _EarningsChart({required this.earnings});
  final List<MonthlyEarning> earnings;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.borderLight),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: const [
              Text(
                'Monthly Earnings',
                style: TextStyle(
                  fontFamily: 'DMSans',
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textPrimary,
                ),
              ),
              Text(
                '2024',
                style: TextStyle(
                  fontFamily: 'DMSans',
                  fontSize: 13,
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 18),
          SizedBox(
            height: 130,
            child: _BarChart(earnings: earnings),
          ),
        ],
      ),
    );
  }
}

class _BarChart extends StatelessWidget {
  const _BarChart({required this.earnings});
  final List<MonthlyEarning> earnings;

  @override
  Widget build(BuildContext context) {
   if (earnings.isEmpty) return const SizedBox.shrink();

final maxAmount = earnings.map((e) => e.amount).reduce(math.max);

    return Row(
      crossAxisAlignment: CrossAxisAlignment.end,
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: earnings.asMap().entries.map((entry) {
        final i = entry.key;
        final e = entry.value;
        final ratio = e.amount / maxAmount;
        final isHighlighted = i == 0; // Jan highlighted

        return Column(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            Expanded(
              child: Align(
                alignment: Alignment.bottomCenter,
                child: AnimatedContainer(
                  duration: Duration(milliseconds: 300 + (i * 80)),
                  curve: Curves.easeOut,
                  width: 28,
                  height: 100 * ratio,
                  decoration: BoxDecoration(
                    color: isHighlighted
                        ? AppColors.accentYellow
                        : AppColors.primaryGreen,
                    borderRadius: BorderRadius.circular(6),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              e.month,
              style: const TextStyle(
                fontFamily: 'DMSans',
                fontSize: 11,
                color: AppColors.textSecondary,
              ),
            ),
          ],
        );
      }).toList(),
    );
  }
}

// ─────────────────────────── Transaction History ────────────────────────────

class _TransactionHistory extends StatelessWidget {
  const _TransactionHistory({required this.transactions});
  final List<WalletTransaction> transactions;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'Transaction History',
              style: TextStyle(
                fontFamily: 'DMSans',
                fontSize: 16,
                fontWeight: FontWeight.w700,
                color: AppColors.textPrimary,
              ),
            ),
            GestureDetector(
              onTap: () {},
              child: const Text(
                'See All',
                style: TextStyle(
                  fontFamily: 'DMSans',
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: AppColors.primaryGreen,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        ...transactions.map((tx) => _TransactionTile(transaction: tx)),
      ],
    );
  }
}

class _TransactionTile extends StatelessWidget {
  const _TransactionTile({required this.transaction});
  final WalletTransaction transaction;

  @override
  Widget build(BuildContext context) {
    final isDebit = transaction.type == TransactionType.withdrawal;
    final amountColor = isDebit ? AppColors.accentRed : AppColors.primaryGreen;
    final amountPrefix = isDebit ? '-' : '+';
    final absAmount = transaction.amount.abs();
    final statusLabel = isDebit ? 'Sent' : 'Paid';
    final icon = isDebit ? Icons.arrow_upward_rounded : Icons.check_circle_rounded;
    final iconBg = isDebit ? AppColors.accentRed : AppColors.primaryGreen;

    final title = transaction.subtitle.isNotEmpty
        ? '${transaction.title} · ${transaction.subtitle}'
        : transaction.title;

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppColors.borderLight),
      ),
      child: Row(
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: iconBg,
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: Colors.white, size: 17),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontFamily: 'DMSans',
                    fontSize: 13.5,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  Formatters.shortDate(transaction.date),
                  style: const TextStyle(
                    fontFamily: 'DMSans',
                    fontSize: 11.5,
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '$amountPrefix${Formatters.naira(absAmount)}',
                style: TextStyle(
                  fontFamily: 'DMSans',
                  fontSize: 13.5,
                  fontWeight: FontWeight.w700,
                  color: amountColor,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                statusLabel,
                style: TextStyle(
                  fontFamily: 'DMSans',
                  fontSize: 11,
                  fontWeight: FontWeight.w500,
                  color: amountColor,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}