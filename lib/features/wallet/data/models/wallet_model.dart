enum TransactionType { credit, debit, escrowLock, withdrawal }
enum TransactionStatus { completed, pending, failed }

class WalletBalance {
  const WalletBalance({
    required this.available,
    required this.locked,
    required this.totalEarned,
    required this.thisMonth,
  });

  final int available;   // kobo
  final int locked;      // kobo (escrow held)
  final int totalEarned; // kobo
  final int thisMonth;   // kobo

  factory WalletBalance.mock() => const WalletBalance(
        available: 4735000,   // ₦47,350
        locked: 850000,       // ₦8,500
        totalEarned: 6300000, // ₦63,000 (used for "This Month")
        thisMonth: 6300000,
      );
}

class WorkerStats {
  const WorkerStats({
    required this.jobsDone,
    required this.avgPerJob,
    required this.rating,
  });

  final int jobsDone;
  final int avgPerJob; // kobo
  final double rating;

  factory WorkerStats.mock() => const WorkerStats(
        jobsDone: 14,
        avgPerJob: 450000, // ₦4,500
        rating: 4.8,
      );
}

class MonthlyEarning {
  const MonthlyEarning({required this.month, required this.amount});
  final String month;
  final int amount; // kobo
}

class WalletTransaction {
  const WalletTransaction({
    required this.id,
    required this.title,
    required this.subtitle,
    required this.date,
    required this.amount,
    required this.type,
    required this.status,
  });

  final String id;
  final String title;
  final String subtitle;
  final DateTime date;
  final int amount; // kobo (negative for debit)
  final TransactionType type;
  final TransactionStatus status;

  bool get isCredit =>
      type == TransactionType.credit || type == TransactionType.escrowLock;
}

class WalletState {
  const WalletState({
    required this.balance,
    required this.stats,
    required this.monthlyEarnings,
    required this.transactions,
  });

  final WalletBalance balance;
  final WorkerStats stats;
  final List<MonthlyEarning> monthlyEarnings;
  final List<WalletTransaction> transactions;

  factory WalletState.mock() => WalletState(
        balance: WalletBalance.mock(),
        stats: WorkerStats.mock(),
        monthlyEarnings: const [
          MonthlyEarning(month: 'Jan', amount: 6200000),
          MonthlyEarning(month: 'Feb', amount: 5100000),
          MonthlyEarning(month: 'Mar', amount: 4800000),
          MonthlyEarning(month: 'Apr', amount: 3900000),
          MonthlyEarning(month: 'May', amount: 5300000),
          MonthlyEarning(month: 'Jun', amount: 2100000),
        ],
        transactions: [
          WalletTransaction(
            id: '1',
            title: 'AC Technician',
            subtitle: 'ChillZone',
            date: DateTime(2024, 1, 15),
            amount: 850000,
            type: TransactionType.credit,
            status: TransactionStatus.completed,
          ),
          WalletTransaction(
            id: '2',
            title: 'Van Driver',
            subtitle: 'LogisticsPro',
            date: DateTime(2024, 1, 12),
            amount: 1500000,
            type: TransactionType.credit,
            status: TransactionStatus.completed,
          ),
          WalletTransaction(
            id: '3',
            title: 'Withdrawal to GTBank',
            subtitle: '',
            date: DateTime(2024, 1, 10),
            amount: -2000000,
            type: TransactionType.withdrawal,
            status: TransactionStatus.completed,
          ),
        ],
      );
}