import 'package:dio/dio.dart';
import '../../storage/secure_storage.dart';

class ErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      // Token expired — clear session, router guard will redirect to login
      await SecureStorage.clearSession();
    }
    handler.next(err);
  }
}