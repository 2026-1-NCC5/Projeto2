import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/readings_api.dart';
import '../../../core/providers/app_provider.dart';
import '../../../core/theme/app_colors.dart';

class FoodRegisterPage extends StatefulWidget {
  const FoodRegisterPage({super.key});

  @override
  State<FoodRegisterPage> createState() => _FoodRegisterPageState();
}

class _FoodRegisterPageState extends State<FoodRegisterPage> {
  final _controllers = {
    FoodCategory.arroz: TextEditingController(),
    FoodCategory.feijao: TextEditingController(),
    FoodCategory.macarrao: TextEditingController(),
    FoodCategory.acucar: TextEditingController(),
    FoodCategory.outros: TextEditingController(),
  };

  bool _loading = false;

  @override
  void dispose() {
    for (final c in _controllers.values) {
      c.dispose();
    }
    super.dispose();
  }

  ReadingsApi _api(BuildContext context) {
    final appProvider = Provider.of<AppProvider>(context, listen: false);
    final client = ApiClient();
    client.setToken(appProvider.token);
    return ReadingsApi(client);
  }

  Future<void> _submit() async {
    final appProvider = Provider.of<AppProvider>(context, listen: false);
    final team = appProvider.activeTeam;

    if (team == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Nenhuma equipe associada ao usuário')),
      );
      return;
    }

    final entries = <MapEntry<FoodCategory, double>>[];
    for (final entry in _controllers.entries) {
      final val = double.tryParse(entry.value.text.trim().replaceAll(',', '.'));
      if (val != null && val > 0) {
        entries.add(MapEntry(entry.key, val));
      }
    }

    if (entries.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Informe ao menos uma quantidade acima de 0')),
      );
      return;
    }

    setState(() => _loading = true);

    try {
      final api = _api(context);
      for (final entry in entries) {
        await api.createReading(
          teamId: team.id,
          category: foodCategoryToString(entry.key),
          kgAmount: entry.value,
        );
      }

      for (final c in _controllers.values) {
        c.clear();
      }

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          backgroundColor: AppColors.green,
          content: Text('${entries.length} registro(s) enviado(s) com sucesso!'),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao registrar: $e')),
      );
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Widget _buildField(FoodCategory category) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: TextField(
        controller: _controllers[category],
        keyboardType: const TextInputType.numberWithOptions(decimal: true),
        decoration: InputDecoration(
          labelText: foodCategoryLabel(category),
          suffixText: 'kg',
          border: const OutlineInputBorder(),
          prefixIcon: const Icon(Icons.scale),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final appProvider = Provider.of<AppProvider>(context);
    final width = MediaQuery.of(context).size.width;
    final isWide = width > 600;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Registrar Alimentos'),
        centerTitle: true,
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pushReplacementNamed(context, appProvider.homeRoute),
        ),
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: isWide ? 520 : double.infinity),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Card(
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  child: ListTile(
                    leading: Icon(Icons.groups, color: AppColors.primary),
                    title: const Text('Equipe'),
                    subtitle: Text(
                      appProvider.activeTeam?.name ?? 'Nenhuma equipe',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Card(
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Quilos coletados',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: AppColors.primary,
                          ),
                        ),
                        const SizedBox(height: 8),
                        for (final cat in FoodCategory.values) _buildField(cat),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 20),
                SizedBox(
                  height: 52,
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primary,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    onPressed: _loading ? null : _submit,
                    icon: _loading
                        ? const SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                          )
                        : const Icon(Icons.check_circle_outline),
                    label: Text(
                      _loading ? 'Enviando...' : 'Registrar',
                      style: const TextStyle(fontSize: 16),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
