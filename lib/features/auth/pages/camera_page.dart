import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
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
  final ImagePicker _picker = ImagePicker();
  File? _photo;

  bool _loading = false;
  String? _predCategory;
  double? _predConfidence;

  Future<void> takePhoto() async {
    final file = await _picker.pickImage(source: ImageSource.camera, imageQuality: 80);
    if (file == null) return;

    setState(() {
      _photo = File(file.path);
      _predCategory = null;
      _predConfidence = null;
    });
  }

  Future<void> predictAndSave() async {
    final appProvider = Provider.of<AppProvider>(context, listen: false);

    if (appProvider.activeTeam == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Selecione uma equipe antes de registrar leituras')),
      );
      return;
    }
    if (_photo == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Tire uma foto antes')),
      );
      return;
    }

    setState(() => _loading = true);

    try {
      final api = ReadingsApi(ApiClient());

      final pred = await api.predict(_photo!);
      final category = pred['category'] as String; // arroz/feijao/outros
      final confidence = (pred['confidence'] as num).toDouble();

      setState(() {
        _predCategory = category;
        _predConfidence = confidence;
      });

      await api.createReading(
        teamId: appProvider.activeTeam!.id,
        category: category,
        confidence: confidence,
      );

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          backgroundColor: AppColors.green,
          content: Text('Salvo: $category (conf: $confidence)'),
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro: $e')),
      );
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final appProvider = Provider.of<AppProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Leitura pela Câmera'),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pushReplacementNamed(context, appProvider.homeRoute),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Card(
              child: ListTile(
                leading: const Icon(Icons.groups),
                title: const Text('Equipe ativa'),
                subtitle: Text(appProvider.activeTeam?.name ?? 'Nenhuma'),
              ),
            ),
            const SizedBox(height: 12),

            if (_photo != null)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    children: [
                      ClipRRect(
                        borderRadius: BorderRadius.circular(12),
                        child: Image.file(
                          _photo!,
                          height: 240,
                          width: double.infinity,
                          fit: BoxFit.cover,
                        ),
                      ),
                      const SizedBox(height: 12),
                      if (_predCategory != null)
                        Text(
                          'Predição: $_predCategory (conf: ${_predConfidence?.toStringAsFixed(2)})',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                      const SizedBox(height: 12),
                      SizedBox(
                        width: double.infinity,
                        height: 48,
                        child: ElevatedButton.icon(
                          style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary),
                          icon: _loading
                              ? const SizedBox(
                                  width: 18,
                                  height: 18,
                                  child: CircularProgressIndicator(strokeWidth: 2),
                                )
                              : const Icon(Icons.auto_awesome),
                          label: Text(_loading ? 'Processando...' : 'Enviar e Registrar'),
                          onPressed: _loading ? null : predictAndSave,
                        ),
                      ),
                    ],
                  ),
                ),
              )
            else
              Card(
                child: ListTile(
                  leading: const Icon(Icons.camera_alt, size: 30),
                  title: const Text('Tirar foto'),
                  subtitle: const Text('Abrir câmera e capturar leitura'),
                  onTap: takePhoto,
                ),
              ),

            const SizedBox(height: 12),

            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton.icon(
                style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary),
                icon: const Icon(Icons.camera_alt),
                label: Text(_photo == null ? 'Abrir câmera' : 'Tirar outra foto'),
                onPressed: takePhoto,
              ),
            ),
          ],
        ),
      ),
    );
  }
}