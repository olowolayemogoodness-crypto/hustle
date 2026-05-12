import 'package:supabase_flutter/supabase_flutter.dart' show User;

class AuthUser {
  const AuthUser({
    required this.id,
    required this.phone,
    this.email,
    this.role,
    this.kycStatus = 'unverified',
    this.fullName,
    this.avatarUrl,
    this.isNewUser = false,
  });

  final String  id;
  final String? phone;
  final String? email;
  final String? role;
  final String  kycStatus;
  final String? fullName;
  final String? avatarUrl;
  final bool    isNewUser;

  bool get isWorker   => role == 'worker';
  bool get isEmployer => role == 'employer';
  bool get needsRole  => role == null || role!.isEmpty;
  bool get isVerified => kycStatus == 'verified';

  factory AuthUser.fromSupabase(User user, {bool isNew = false}) {
    final meta = user.userMetadata ?? {};
    return AuthUser(
      id:        user.id,
      phone:     user.phone,
      email:     user.email,
      role:      meta['role']       as String?,
      kycStatus: meta['kyc_status'] as String? ?? 'unverified',
      fullName:  meta['full_name']  as String?,
      avatarUrl: meta['avatar_url'] as String?,
      isNewUser: isNew,
    );
  }

  AuthUser copyWith({String? role, String? kycStatus}) => AuthUser(
    id:        id,
    phone:     phone,
    email:     email,
    role:      role      ?? this.role,
    kycStatus: kycStatus ?? this.kycStatus,
    fullName:  fullName,
    avatarUrl: avatarUrl,
  );
}