import 'dart:async';
import 'dart:io';

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/readings_api.dart';
import '../../../core/providers/app_provider.dart';
import '../../../core/theme/app_colors.dart';

class CameraPage extends StatefulWidget {
  const CameraPage({super.key});

  @override
  State<CameraPage> createState() => _CameraPageState();
}

class _CameraPageState extends State<CameraPage> {
  CameraController? _controller;
  bool _loading = true;
  bool _isCapturing = false;
  bool _isProcessing = false;

  Timer? _captureTimer;

  String _predCategory = '--';
  double _predConfidence = 0.0;

  String? _stableLabel;
  int _stableCount = 0;

  String? _lastConfirmedLabel;
  DateTime? _lastConfirmedAt;

  static const double confidenceThreshold = 0.60;
  static const int requiredFrames = 5;
  static const int cooldownSeconds = 3;
  static const Duration captureInterval = Duration(milliseconds: 900);

  @override
  void initState() {
    super.initState();
    _initCamera();
  }

  ReadingsApi _api(BuildContext context) {
    final appProvider = Provider.of<AppProvider>(context, listen: false);
    final client = ApiClient();
    client.setToken(appProvider.token);
    return ReadingsApi(client);
  }

  Future<void> _initCamera() async {
    try {
      final cameras = await availableCameras();

      final selectedCamera = cameras.firstWhere(
        (c) => c.lensDirection == CameraLensDirection.back,
        orElse: () => cameras.first,
      );

      _controller = CameraController(
        selectedCamera,
        ResolutionPreset.medium,
        enableAudio: false,
      );

      await _controller!.initialize();
      _startAutomaticCapture();

      if (!mounted) return;
      setState(() {
        _loading = false;
      });
    } catch (e) {
      debugPrint('Erro ao iniciar câmera: $e');

      if (!mounted) return;
      setState(() {
        _loading = false;
        _predCategory = 'Erro na câmera';
      });
    }
  }

  void _startAutomaticCapture() {
    _captureTimer?.cancel();

    _captureTimer = Timer.periodic(captureInterval, (_) async {
      if (_isCapturing || _isProcessing) return;
      if (_controller == null || !_controller!.value.isInitialized) return;

      await _captureAndPredict();
    });
  }

  Future<void> _captureAndPredict() async {
    if (_controller == null) return;

    _isCapturing = true;

    try {
      final XFile xfile = await _controller!.takePicture();
      final file = File(xfile.path);

      _isProcessing = true;

      final result = await _api(context).predict(file);

      if (!mounted) return;

      setState(() {
        _predCategory = result['category'];
        _predConfidence = (result['confidence'] as num).toDouble();
      });

      _handlePrediction(
        category: result['category'],
        confidence: (result['confidence'] as num).toDouble(),
      );

      try {
        if (await file.exists()) {
          await file.delete();
        }
      } catch (_) {}
    } catch (e) {
      debugPrint('Erro ao capturar/predizer: $e');
    } finally {
      _isCapturing = false;
      _isProcessing = false;
    }
  }

  void _handlePrediction({
    required String category,
    required double confidence,
  }) {
    if (confidence < confidenceThreshold) {
      setState(() {
        _stableLabel = null;
        _stableCount = 0;
      });
      return;
    }

    if (_stableLabel == category) {
      setState(() {
        _stableCount++;
      });
    } else {
      setState(() {
        _stableLabel = category;
        _stableCount = 1;
      });
    }

    if (_stableCount >= requiredFrames) {
      setState(() {
        _stableCount = 0;
      });

      _confirmReading(category: category, confidence: confidence);
    }
  }

  Future<void> _confirmReading({
    required String category,
    required double confidence,
  }) async {
    final appProvider = Provider.of<AppProvider>(context, listen: false);
    final now = DateTime.now();

    if (_lastConfirmedLabel == category &&
        _lastConfirmedAt != null &&
        now.difference(_lastConfirmedAt!).inSeconds <= cooldownSeconds) {
      return;
    }

    if (appProvider.activeTeam == null) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Selecione uma equipe antes de registrar leituras'),
        ),
      );
      return;
    }

    _lastConfirmedLabel = category;
    _lastConfirmedAt = now;

    try {
      await _api(context).createReading(
        teamId: appProvider.activeTeam!.id,
        category: category,
        confidence: confidence,
        imagePath: null,
      );

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Leitura confirmada: $category (${(confidence * 100).toStringAsFixed(0)}%)',
          ),
          duration: const Duration(seconds: 1),
        ),
      );
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao salvar leitura: $e')),
      );
    }
  }

  @override
  void dispose() {
    _captureTimer?.cancel();
    _controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_loading || _controller == null || !_controller!.value.isInitialized) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: const Text('Leitura Automática'),
        backgroundColor: AppColors.primary,
      ),
      body: Stack(
        children: [
          Positioned.fill(child: CameraPreview(_controller!)),
          Positioned(
            left: 16,
            right: 16,
            bottom: 24,
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.black.withOpacity(0.65),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'Categoria: $_predCategory',
                    style: const TextStyle(fontSize: 18, color: Colors.white),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Confiança: ${(_predConfidence * 100).toStringAsFixed(1)}%',
                    style: const TextStyle(fontSize: 16, color: Colors.white),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Estabilidade: $_stableCount / $requiredFrames',
                    style: const TextStyle(fontSize: 14, color: Colors.white70),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}