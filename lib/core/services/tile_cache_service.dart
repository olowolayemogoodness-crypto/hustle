import 'dart:io';
import 'package:dio_cache_interceptor_hive_store/dio_cache_interceptor_hive_store.dart';
import 'package:flutter_map_cache/flutter_map_cache.dart';
import 'package:path_provider/path_provider.dart';

class TileCacheService {
  TileCacheService._();

  static HiveCacheStore? _store;
  static late String _cachePath;

  /// Must be called once in main() before the app launches
  static Future<void> init() async {
    final dir = await getApplicationCacheDirectory();
    _cachePath = '${dir.path}/osm_tiles';
    await Directory(_cachePath).create(recursive: true);
    _store = HiveCacheStore(
      _cachePath,
      hiveBoxName: 'locgig_tiles',
    );
  }

  /// Returns a CachedTileProvider configured for offline-first usage.
  /// Tiles are cached 30 days — long enough for rural workers to work offline.
  static CachedTileProvider buildProvider() {
    assert(_store != null, 'TileCacheService.init() must be called first');
    return CachedTileProvider(
      store: _store!,
      maxStale: const Duration(days: 30),
    );
  }

  /// Pre-download tiles for a bounding box — call before worker goes offline.
  /// E.g. call when worker opens app on WiFi to cache their LGA area.
  static HiveCacheStore get store => _store!;

  static Future<void> clearCache() async {
    await _store?.clean();
  }
}