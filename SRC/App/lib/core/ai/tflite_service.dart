import 'package:camera/camera.dart';
import 'package:flutter/services.dart';
import 'package:image/image.dart' as img;
import 'package:tflite_flutter/tflite_flutter.dart';

class PredictionResult {
  final String category;
  final double confidence;

  PredictionResult({
    required this.category,
    required this.confidence,
  });
}

class TfliteService {
  Interpreter? _interpreter;
  List<String> _labels = [];

  int inputWidth = 224;
  int inputHeight = 224;
  int inputChannels = 3;

  bool get isLoaded => _interpreter != null;

  Future<void> load() async {
    _interpreter = await Interpreter.fromAsset('assets/model/model.tflite');
    _labels = await _loadLabels('assets/model/labels.txt');

    final inputShape = _interpreter!.getInputTensor(0).shape;
    if (inputShape.length == 4) {
      inputHeight = inputShape[1];
      inputWidth = inputShape[2];
      inputChannels = inputShape[3];
    }
  }

  Future<List<String>> _loadLabels(String path) async {
    final raw = await rootBundle.loadString(path);
    return raw
        .split('\n')
        .map((e) => e.trim())
        .where((e) => e.isNotEmpty)
        .toList();
  }

  Future<PredictionResult?> predictFromCameraImage(CameraImage cameraImage) async {
    if (_interpreter == null) return null;

    final img.Image? converted = _cameraImageToImage(cameraImage);
    if (converted == null) return null;

    final img.Image resized = img.copyResize(
      converted,
      width: inputWidth,
      height: inputHeight,
    );

    final input = [
      List.generate(inputHeight, (y) {
        return List.generate(inputWidth, (x) {
          final pixel = resized.getPixel(x, y);
          final r = pixel.r / 255.0;
          final g = pixel.g / 255.0;
          final b = pixel.b / 255.0;
          return [r, g, b];
        });
      })
    ];

    final outputShape = _interpreter!.getOutputTensor(0).shape;
    final output = List.generate(
      outputShape[0],
      (_) => List.filled(outputShape[1], 0.0),
    );

    _interpreter!.run(input, output);

    final scores = output[0];
    if (scores.isEmpty) return null;

    int bestIndex = 0;
    double bestScore = (scores[0] as num).toDouble();

    for (int i = 1; i < scores.length; i++) {
      final score = (scores[i] as num).toDouble();
      if (score > bestScore) {
        bestScore = score;
        bestIndex = i;
      }
    }

    final label = bestIndex < _labels.length ? _labels[bestIndex] : 'outros';

    return PredictionResult(
      category: _normalizeLabel(label),
      confidence: bestScore,
    );
  }

  img.Image? _cameraImageToImage(CameraImage cameraImage) {
    try {
      if (cameraImage.format.group == ImageFormatGroup.bgra8888) {
        return _convertBGRA8888(cameraImage);
      }

      if (cameraImage.format.group == ImageFormatGroup.yuv420) {
        return _convertYUV420(cameraImage);
      }

      return null;
    } catch (_) {
      return null;
    }
  }

  img.Image _convertBGRA8888(CameraImage image) {
    final plane = image.planes[0];
    return img.Image.fromBytes(
      width: image.width,
      height: image.height,
      bytes: plane.bytes.buffer,
      order: img.ChannelOrder.bgra,
    );
  }

  img.Image _convertYUV420(CameraImage image) {
    final width = image.width;
    final height = image.height;
    final out = img.Image(width: width, height: height);

    final uvRowStride = image.planes[1].bytesPerRow;
    final uvPixelStride = image.planes[1].bytesPerPixel ?? 1;

    for (int y = 0; y < height; y++) {
      final uvRow = uvRowStride * (y >> 1);

      for (int x = 0; x < width; x++) {
        final uvIndex = uvRow + (x >> 1) * uvPixelStride;
        final index = y * image.planes[0].bytesPerRow + x;

        final yp = image.planes[0].bytes[index];
        final up = image.planes[1].bytes[uvIndex];
        final vp = image.planes[2].bytes[uvIndex];

        int r = (yp + vp * 1436 / 1024 - 179).round();
        int g = (yp - up * 46549 / 131072 + 44 - vp * 93604 / 131072 + 91).round();
        int b = (yp + up * 1814 / 1024 - 227).round();

        r = r.clamp(0, 255);
        g = g.clamp(0, 255);
        b = b.clamp(0, 255);

        out.setPixelRgb(x, y, r, g, b);
      }
    }

    return out;
  }

  String _normalizeLabel(String label) {
    final clean = label.trim().toLowerCase();

    switch (clean) {
      case 'arroz':
        return 'arroz';
      case 'feijao':
      case 'feijão':
        return 'feijao';
      case 'acucar':
      case 'açúcar':
        return 'acucar';
      case 'cafe':
      case 'café':
        return 'cafe';
      case 'outros':
        return 'outros';
      default:
        return clean;
    }
  }

  void close() {
    _interpreter?.close();
    _interpreter = null;
  }
}