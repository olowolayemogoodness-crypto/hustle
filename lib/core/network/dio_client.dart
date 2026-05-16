// lib/core/network/dio_client.dart
import 'package:dio/dio.dart';
import 'package:hustle/core/env.dart';
import 'interceptors/auth_interceptor.dart';

class DioClient {
  DioClient._();

  static Dio? _instance;

  static Dio get instance {
    _instance ??= _build();
    return _instance!;
  }

  static Dio _build() {
    final dio = Dio(
      BaseOptions(
        baseUrl:        Env.apiBaseUrl,
        connectTimeout: const Duration(seconds: 15),
        receiveTimeout: const Duration(seconds: 20),
        headers: {
          'Content-Type': 'application/json',
          'Accept':       'application/json',
        },
      ),
    );

    dio.interceptors.add(AuthInterceptor());

    return dio;
  }
}