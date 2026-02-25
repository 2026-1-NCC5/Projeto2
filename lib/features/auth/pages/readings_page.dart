import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/providers/app_provider.dart';

class ReadingsPage extends StatelessWidget {
  const ReadingsPage({super.key});

  String _formatDateTime(DateTime d) {
    final dd = d.day.toString().padLeft(2, '0');
    final mm = d.month.toString().padLeft(2, '0');
    final yyyy = d.year.toString();
    final hh = d.hour.toString().padLeft(2, '0');
    final min = d.minute.toString().padLeft(2, '0');
    return '$dd/$mm/$yyyy $hh:$min';
  }

  @override
  Widget build(BuildContext context) {
    final appProvider = Provider.of<AppProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Dados da Leitura'),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pushReplacementNamed(context, appProvider.homeRoute),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: appProvider.readings.isEmpty
            ? const Center(child: Text('Nenhuma leitura registrada'))
            : ListView.separated(
                itemCount: appProvider.readings.length,
                separatorBuilder: (_, __) => const SizedBox(height: 8),
                itemBuilder: (context, index) {
                  final r = appProvider.readings[index];
                  return Card(
                    child: ListTile(
                      leading: const Icon(Icons.receipt_long),
                      title: Text('${r.teamName} • ${foodCategoryLabel(r.category)}'),
                      subtitle: Text('Operador: ${r.operatorName} • ${_formatDateTime(r.timestamp)}'),
                    ),
                  );
                },
              ),
      ),
    );
  }
}