
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hustle/core/services/nominatim_service.dart';

import 'package:latlong2/latlong.dart';
import '../../../jobs/data/models/job_model.dart';


import '../../../../core/config/app_config.dart';
import '../../../../core/config/theme.dart';
import '../../../../core/services/osrm_service.dart';
import '../../../../core/services/tile_cache_service.dart';
import '../../../../core/utils/formatters.dart';


import '../providers/jobs_provider.dart';
import '../providers/location_provider.dart';
import '../providers/map_provider.dart';

class MapViewScreen extends ConsumerStatefulWidget {
  const MapViewScreen({super.key});

  @override
  ConsumerState<MapViewScreen> createState() => _MapViewScreenState();
}

class _MapViewScreenState extends ConsumerState<MapViewScreen>
    with TickerProviderStateMixin {
  late final MapController _mapController;
  late final AnimationController _pulseController;
  late final Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _mapController = MapController();

    // Pulsing animation for user location dot
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat(reverse: true);

    _pulseAnimation = Tween<double>(begin: 0.6, end: 1.0).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );

    // Listen to location updates for map following
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.listenManual(locationProvider, (_, next) {
        next.whenData((latLng) {
          if (latLng != null) {
            final mapState = ref.read(mapProvider);
            if (mapState.isFollowingUser) {
              _mapController.move(latLng, _mapController.camera.zoom);
            }
          }
        });
      });
    });
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _mapController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final jobsAsync = ref.watch(jobsProvider);
    final mapState = ref.watch(mapProvider);

    return Scaffold(
      body: Stack(
        children: [
          // ── 1. Full-screen Map ──
          jobsAsync.when(
            loading: () => _buildMap([], mapState),
            error: (_, __) => _buildMap([], mapState),
            data: (jobs) => _buildMap(jobs, mapState),
          ),

          // ── 2. Status bar safe area ──
          const _TopSafeArea(),

          // ── 3. Search overlay bar ──
          Positioned(
            top: MediaQuery.of(context).padding.top + 8,
            left: 16,
            right: 16,
            child:  _MapSearchBar(mapController: _mapController),
          ),

          // ── 4. Recenter FAB ──
          Positioned(
            right: 16,
            bottom: 280,
            child: _RecenterButton(
              isFollowing: mapState.isFollowingUser,
              onTap: () {
                ref.read(mapProvider.notifier).recenterOnUser();
                final pos = mapState.userPosition ?? kDefaultLagosCenter;
                _mapController.move(pos, 14.0);
              },
            ),
          ),

          // ── 5. Draggable bottom sheet with job cards ──
        // ── 5. Draggable bottom sheet with job cards ──
Positioned.fill(
  child: Padding(
    padding: EdgeInsets.only(
      bottom: MediaQuery.of(context).viewInsets.bottom, // ← shrinks when keyboard opens
    ),
    child: jobsAsync.when(
      loading: () => _NearbyJobsSheet(jobs: [], selectedId: null),
      error: (_, __) => _NearbyJobsSheet(jobs: [], selectedId: null),
      data: (jobs) => _NearbyJobsSheet(
        jobs: jobs,
        selectedId: mapState.selectedJobId,
      ),
    ),
  ),
),

          // ── 6. Bottom nav ──

        ],
      ),
    );
  }

  Widget _buildMap(List<JobListing> jobs, MapState mapState) {
    return FlutterMap(
      mapController: _mapController,
      options: MapOptions(
        initialCenter: mapState.userPosition ?? kDefaultLagosCenter,
        initialZoom: kDefaultZoom,
        minZoom: 10,
        maxZoom: 18,
        interactionOptions: const InteractionOptions(
          flags: InteractiveFlag.all & ~InteractiveFlag.rotate,
        ),
        onTap: (_, __) {
          // Deselect marker on map tap
          ref.read(mapProvider.notifier).clearSelection();
        },
        onMapEvent: (event) {


          // Stop following user when they manually pan
          if (event is MapEventScrollWheelZoom ||
              event is MapEventMove) {
            if (event.source == MapEventSource.dragStart) {
              ref.read(mapProvider.notifier).stopFollowingUser();
            }
          }
        },
      ),
      children: [
        // ── OSM Tile Layer with Hive cache ──
        TileLayer(
          urlTemplate: AppConfig.tileUrlTemplate,
          tileProvider: TileCacheService.buildProvider(),
          userAgentPackageName: 'app.locgig.mobile',
          maxNativeZoom: 18,
          // Fallback to OSM when offline cache misses
          fallbackUrl: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        ),

        // ── Job Price Pin Markers ──
        MarkerLayer(
          markers: jobs.map((job) {
            final isSelected = job.id == mapState.selectedJobId;
            return Marker(
              point: LatLng(job.latitude, job.longitude),
              width: isSelected ? 170 : 90,
              height: isSelected ? 74 : 36,
              alignment: Alignment.bottomCenter,
              child: GestureDetector(
                onTap: () {
                  ref.read(mapProvider.notifier).selectJob(job.id);
                  _mapController.move(
                    LatLng(job.latitude, job.longitude),
                    15.5,
                  );
                },
                child: _PricePin(job: job, isSelected: isSelected),
              ),
            );
          }).toList(),
        ),
// In _buildMap — add after MarkerLayer
if (mapState.routePoints.isNotEmpty)
  PolylineLayer(
    polylines: [
      Polyline(
        points: mapState.routePoints,
        strokeWidth: 4.0,
        color: AppColors.primaryGreen,
        borderStrokeWidth: 1.5,
        borderColor: Colors.white,
      ),
    ],
  ),
        // ── User Location Marker ──
        if (mapState.userPosition != null)
          MarkerLayer(
            markers: [
              Marker(
                point: mapState.userPosition!,
                width: 40,
                height: 40,
                child: AnimatedBuilder(
                  animation: _pulseAnimation,
                  builder: (_, __) =>
                      _UserLocationDot(scale: _pulseAnimation.value),
                ),
              ),
            ],
          ),
      ],
    );
  }
}

// ─────────────────────────── Top Safe Area ────────────────────────────

class _TopSafeArea extends StatelessWidget {
  const _TopSafeArea();

  @override
  Widget build(BuildContext context) {
    return Positioned(
      top: 0,
      left: 0,
      right: 0,
      child: Container(
        height: MediaQuery.of(context).padding.top,
        color: Colors.white.withOpacity(0.9),
      ),
    );
  }
}

// ─────────────────────────── Map Search Bar ────────────────────────────

class _MapSearchBar extends ConsumerStatefulWidget {
  const _MapSearchBar({required this.mapController}); // ← add
  final MapController mapController;  
  @override
  ConsumerState<_MapSearchBar> createState() => _MapSearchBarState();
}

class _MapSearchBarState extends ConsumerState<_MapSearchBar> {
         
  final _controller = TextEditingController();
  List<NominatimResult> _results = [];
  bool _searching = false;

  Future<void> _onChanged(String query) async {
    if (query.length < 3) {
      setState(() => _results = []);
      return;
    }
    setState(() => _searching = true);
    final results = await NominatimService.search(query);
    setState(() { _results = results; _searching = false; });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Search bar row
        Row(
          children: [
            Expanded(
              child: Container(
                height: 48,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(14),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.12),
                      blurRadius: 12,
                      offset: const Offset(0, 3),
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    const SizedBox(width: 12),
                    _searching
                        ? const SizedBox(
                            width: 18, height: 18,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: AppColors.primaryGreen,
                            ),
                          )
                        : const Icon(Icons.search_rounded,
                            color: AppColors.textSecondary, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: TextField(
                        controller: _controller,
                        onChanged: _onChanged,
                        decoration: const InputDecoration(
                          hintText: 'Search nearby jobs or location...',
                          hintStyle: TextStyle(
                            fontFamily: 'DMSans',
                            fontSize: 13.5,
                            color: AppColors.textHint,
                          ),
                          border: InputBorder.none,
                          isDense: true,
                          contentPadding: EdgeInsets.zero,
                        ),
                      ),
                    ),
                    if (_controller.text.isNotEmpty)
                      GestureDetector(
                        onTap: () {
                          _controller.clear();
                          setState(() => _results = []);
                        },
                        child: const Padding(
                          padding: EdgeInsets.all(8),
                          child: Icon(Icons.close_rounded,
                              size: 18, color: AppColors.textSecondary),
                        ),
                      ),
                  ],
                ),
              ),
            ),
            const SizedBox(width: 10),
            Container(
              width: 48, height: 48,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(14),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.12),
                    blurRadius: 12,
                    offset: const Offset(0, 3),
                  ),
                ],
              ),
              child: const Icon(Icons.tune_rounded,
                  color: AppColors.textSecondary, size: 22),
            ),
          ],
        ),

        // Search results dropdown
        if (_results.isNotEmpty)
          Container(
            margin: const EdgeInsets.only(top: 6),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(14),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Column(
              children: _results.map((r) => ListTile(
                leading: const Icon(Icons.location_on_outlined,
                    color: AppColors.primaryGreen, size: 20),
                title: Text(
                  r.displayName,
                  style: const TextStyle(
                    fontFamily: 'DMSans',
                    fontSize: 13,
                    color: AppColors.textPrimary,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                onTap: () {
                 
  _controller.clear();
  setState(() => _results = []);
  FocusScope.of(context).unfocus(); // ← dismiss keyboard

  // Animate to location exactly like recenter button
  widget.mapController.move(r.latLng, 15.0); // ← zooms to point
  ref.read(mapProvider.notifier).updateCameraPosition(r.latLng);

                },
              )).toList(),
            ),
          ),
      ],
    );
  }
}

// ─────────────────────────── Price Pin Marker ────────────────────────────

class _PricePin extends StatelessWidget {
  const _PricePin({required this.job, required this.isSelected});
  final JobListing job;
  final bool isSelected;

  @override
  Widget build(BuildContext context) {
    if (isSelected) {
      return _SelectedPin(job: job);
    }
    return _DefaultPin(job: job);
  }
}

class _DefaultPin extends StatelessWidget {
  const _DefaultPin({required this.job});
  final JobListing job;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 90,
      height: 36,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 90,
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
            decoration: BoxDecoration(
              color: AppColors.primaryGreen,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: AppColors.primaryGreen.withOpacity(0.4),
                  blurRadius: 6,
                  offset: const Offset(0, 3),
                ),
              ],
            ),
            child: Center(
              child: Text(
                Formatters.naira(job.payKobo),
                style: const TextStyle(
                  fontFamily: 'Syne',
                  fontSize: 12,
                  fontWeight: FontWeight.w800,
                  color: Colors.white,
                ),
                overflow: TextOverflow.ellipsis,
                maxLines: 1,
              ),
            ),
          ),
          // Pin tail
          CustomPaint(
            size: const Size(10, 6),
            painter: _PinTailPainter(color: AppColors.primaryGreen),
          ),
        ],
      ),
    );
  }
}

class _SelectedPin extends StatelessWidget {
  const _SelectedPin({required this.job});
  final JobListing job;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 170,
      height: 74,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 170,
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 9),
            decoration: BoxDecoration(
              color: AppColors.primaryGreen,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: AppColors.primaryGreen.withOpacity(0.5),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.bolt_rounded,
                      color: job.accentColor.color,
                      size: 13,
                    ),
                    const SizedBox(width: 3),
                    Flexible(
                      child: Text(
                        Formatters.naira(job.payKobo),
                        style: const TextStyle(
                          fontFamily: 'Syne',
                          fontSize: 14,
                          fontWeight: FontWeight.w800,
                          color: Colors.white,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 2),
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Expanded(
                      child: Text(
                        job.title,
                        style: const TextStyle(
                          fontFamily: 'DMSans',
                          fontSize: 10.5,
                          color: Colors.white70,
                          fontWeight: FontWeight.w500,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    Container(
                      margin: const EdgeInsets.only(left: 6),
                      padding: const EdgeInsets.symmetric(
                          horizontal: 5, vertical: 2),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        job.distanceDisplay,
                        style: const TextStyle(
                          fontFamily: 'DMSans',
                          fontSize: 9.5,
                          color: Colors.white,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          CustomPaint(
            size: const Size(12, 7),
            painter: _PinTailPainter(color: AppColors.primaryGreen),
          ),
        ],
      ),
    );
  }
}
class _PinTailPainter extends CustomPainter {
  const _PinTailPainter({required this.color});
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color;
    final path = ui.Path()          // ← explicitly dart:ui Path
      ..moveTo(0, 0)
      ..lineTo(size.width / 2, size.height)
      ..lineTo(size.width, 0)
      ..close();
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(_) => false;
}
// ─────────────────────────── User Location Dot ────────────────────────────

class _UserLocationDot extends StatelessWidget {
  const _UserLocationDot({required this.scale});
  final double scale;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Outer pulse ring
          Transform.scale(
            scale: scale,
            child: Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                color: Colors.blue.withOpacity(0.18),
                shape: BoxShape.circle,
              ),
            ),
          ),
          // White border
          Container(
            width: 18,
            height: 18,
            decoration: const BoxDecoration(
              color: Colors.white,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(color: Colors.black26, blurRadius: 4)
              ],
            ),
          ),
          // Blue core dot
          Container(
            width: 12,
            height: 12,
            decoration: const BoxDecoration(
              color: Color(0xFF2563EB),
              shape: BoxShape.circle,
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────── Recenter Button ────────────────────────────

class _RecenterButton extends StatelessWidget {
  const _RecenterButton({
    required this.isFollowing,
    required this.onTap,
  });
  final bool isFollowing;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 44,
        height: 44,
        decoration: BoxDecoration(
          color: isFollowing ? AppColors.primaryGreen : Colors.white,
          shape: BoxShape.circle,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.15),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Icon(
          Icons.my_location_rounded,
          color: isFollowing ? Colors.white : AppColors.primaryGreen,
          size: 22,
        ),
      ),
    );
  }
}

// ─────────────────────────── Nearby Jobs Bottom Sheet ────────────────────────────
class _NearbyJobsSheet extends StatefulWidget {
  const _NearbyJobsSheet({required this.jobs, required this.selectedId});
  final List<JobListing> jobs;
  final String? selectedId;

  @override
  State<_NearbyJobsSheet> createState() => _NearbyJobsSheetState();
}

class _NearbyJobsSheetState extends State<_NearbyJobsSheet> {
  final _sheetController = DraggableScrollableController();

  @override
  void dispose() {
    _sheetController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final keyboardOpen = MediaQuery.of(context).viewInsets.bottom > 0;

    // Collapse sheet when keyboard opens
    if (keyboardOpen) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (_sheetController.isAttached) {
          _sheetController.animateTo(
            0.0,
            duration: const Duration(milliseconds: 200),
            curve: Curves.easeOut,
          );
        }
      });
    }

    return DraggableScrollableSheet(
      controller: _sheetController,
      initialChildSize: keyboardOpen ? 0.0 : 0.30,
      minChildSize: 0.07,           // ← prevents full collapse
      maxChildSize: 0.55,
      snap: true,
      snapSizes: const [0.07, 0.25, 0.30, 0.55],
      builder: (context, scrollController) {
        return Container(
          decoration: const BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.vertical(top: Radius.circular(22)),
            boxShadow: [
              BoxShadow(
                color: Colors.black12,
                blurRadius: 16,
                offset: Offset(0, -4),
              ),
            ],
          ),
          child: SingleChildScrollView(
            controller: scrollController,
            physics: const ClampingScrollPhysics(),
            child: Column(
              children: [
                // Drag handle
                Padding(
                  padding: const EdgeInsets.only(top: 10, bottom: 4),
                  child: Container(
                    width: 38,
                    height: 4,
                    decoration: BoxDecoration(
                      color: AppColors.borderLight,
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                ),
                // Header
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
                  child: Row(
                    children: [
                      Container(
                        width: 8, height: 8,
                        decoration: const BoxDecoration(
                          color: AppColors.success,
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        '${widget.jobs.length} Jobs Near You',
                        style: const TextStyle(
                          fontFamily: 'DMSans',
                          fontSize: 15,
                          fontWeight: FontWeight.w700,
                          color: AppColors.textPrimary,
                        ),
                      ),
                    ],
                  ),
                ),
                // Horizontal job cards
                SizedBox(
                  height: 190,
                  child: ListView.separated(
                    scrollDirection: Axis.horizontal,
                    padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                    itemCount: widget.jobs.length,
                    separatorBuilder: (_, __) => const SizedBox(width: 12),
                    itemBuilder: (context, i) => _MapJobCard(
                      job: widget.jobs[i],
                      isSelected: widget.jobs[i].id == widget.selectedId,
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}


class _MapJobCard extends ConsumerWidget {
  const _MapJobCard({required this.job, required this.isSelected});
  final JobListing job;
  final bool isSelected;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return GestureDetector(
      onTap: () => ref.read(mapProvider.notifier).selectJob(job.id),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        width: 190,
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isSelected
                ? AppColors.primaryGreen
                : AppColors.borderLight,
            width: isSelected ? 2 : 1,
          ),
          boxShadow: [
            if (isSelected)
              BoxShadow(
                color: AppColors.primaryGreen.withOpacity(0.12),
                blurRadius: 10,
                offset: const Offset(0, 2),
              )
            else
              const BoxShadow(
                color: Colors.black12,
                blurRadius: 6,
                offset: Offset(0, 2),
              ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Title + Distance
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    job.title,
                    style: const TextStyle(
                      fontFamily: 'DMSans',
                      fontSize: 13,
                      fontWeight: FontWeight.w700,
                      color: AppColors.textPrimary,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                const SizedBox(width: 4),
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 7, vertical: 3),
                  decoration: BoxDecoration(
                    color: AppColors.primaryGreenLight,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    job.distanceDisplay,
                    style: const TextStyle(
                      fontFamily: 'DMSans',
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                      color: AppColors.primaryGreen,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 3),
            // Employer
            Text(
              job.employerName,
              style: const TextStyle(
                fontFamily: 'DMSans',
                fontSize: 11.5,
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 8),
            // Pay
            Text(
              Formatters.naira(job.payKobo),
              style: const TextStyle(
                fontFamily: 'Syne',
                fontSize: 16,
                fontWeight: FontWeight.w800,
                color: AppColors.primaryGreen,
              ),
            ),
            const SizedBox(height: 8),
            // Category chip + Apply
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppColors.primaryGreenLight,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.build_circle_outlined,
                          size: 10, color: AppColors.primaryGreen),
                      const SizedBox(width: 3),
                      Text(
                        job.skillRequired
                            .replaceAll('_', ' ')
                            .toCapitalized(),
                        style: const TextStyle(
                          fontFamily: 'DMSans',
                          fontSize: 10,
                          fontWeight: FontWeight.w600,
                          color: AppColors.primaryGreen,
                        ),
                      ),
                    ],
                  ),
                ),
                const Spacer(),
                GestureDetector(
                  onTap: () async {
                    final userPos = ref.read(mapProvider).userPosition;
                    if (userPos == null) return;

                    final route = await OsrmService.getRoute(
                      origin: userPos,
                      destination: LatLng(job.latitude, job.longitude),
                    );

                    if (route != null) {
                      ref.read(mapProvider.notifier).setRoute(route.polylinePoints);
                    }
                  },
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(
                      border: Border.all(
                          color: AppColors.primaryGreen, width: 1.5),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Text(
                      'Apply',
                      style: TextStyle(
                        fontFamily: 'DMSans',
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                        color: AppColors.primaryGreen,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}





// ─────────────────────────── String Extension ────────────────────────────

extension StringUtils on String {
  String toCapitalized() =>
      isNotEmpty ? '${this[0].toUpperCase()}${substring(1)}' : this;
}