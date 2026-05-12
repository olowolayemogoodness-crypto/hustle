import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:hustle/core/supabase/supabase_config.dart';
import 'core/services/tile_cache_service.dart';
import 'app.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  await dotenv.load(fileName: '.env');

  // Hive init — used for tile cache + app storage
  await Hive.initFlutter();

  await SupabaseConfig.init();


  // Prime the tile cache store (Hive box)
  await TileCacheService.init();

  runApp(
    const ProviderScope(
      child: HustleApp(),
    ),
  );
}