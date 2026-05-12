class AuthUser {
  const AuthUser({
    required this.id,
    required this.phone,
    this.role,
    this.kycStatus = 'unverified',
    this.isNewUser = false,
    this.fullName,
    this.avatarUrl,
  });

  final String id;
  final String phone;
  final String? role;
  final String kycStatus;
  final bool isNewUser;
  final String? fullName;
  final String? avatarUrl;

  bool get isWorker   => role == 'worker';
  bool get isEmployer => role == 'employer';
  bool get needsRole  => role == null;
  bool get isVerified => kycStatus == 'verified';

  factory AuthUser.fromJson(Map<String, dynamic> json) => AuthUser(
        id: json['id'] as String,
        phone: json['phone'] as String,
        role: json['role'] as String?,
        kycStatus: json['kyc_status'] as String? ?? 'unverified',
        isNewUser: json['is_new_user'] as bool? ?? false,
        fullName: json['full_name'] as String?,
        avatarUrl: json['avatar_url'] as String?,
      );

  AuthUser copyWith({String? role, String? kycStatus}) => AuthUser(
        id: id,
        phone: phone,
        role: role ?? this.role,
        kycStatus: kycStatus ?? this.kycStatus,
        isNewUser: isNewUser,
        fullName: fullName,
        avatarUrl: avatarUrl,
      );
}

class AuthSession {
  const AuthSession({
    required this.token,
    required this.user,
    required this.expiresIn,
  });

  final String token;
  final AuthUser user;
  final int expiresIn;

  factory AuthSession.fromJson(Map<String, dynamic> json) => AuthSession(
        token: json['access_token'] as String,
        expiresIn: json['expires_in'] as int,
        user: AuthUser.fromJson(json['user'] as Map<String, dynamic>),
      );
}