import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'core/services/tile_cache_service.dart';
import 'app.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Hive init — used for tile cache + app storage
  await Hive.initFlutter();

  // Prime the tile cache store (Hive box)
  await TileCacheService.init();

  runApp(
    const ProviderScope(
      child: HustleApp(),
    ),
  );
}