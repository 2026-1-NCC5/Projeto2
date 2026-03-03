import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/providers/app_provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/export_downloader.dart';

class ExportPage extends StatefulWidget {
  const ExportPage({super.key});

  @override
  State<ExportPage> createState() => _ExportPageState();
}

class _ExportPageState extends State<ExportPage> {
  String teamFilter = 'Todas';
  String categoryFilter = 'Todas';
  DateTime? startDate;
  DateTime? endDate;

  String _formatDate(DateTime? d) {
    if (d == null) return '—';
    return '${d.day.toString().padLeft(2, '0')}/'
        '${d.month.toString().padLeft(2, '0')}/'
        '${d.year}';
  }

  Future<void> pickStartDate() async {
    final initial = startDate ?? DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: initial,
      firstDate: DateTime(2020),
      lastDate: DateTime(2100),
    );
    if (picked == null) return;

    setState(() {
      startDate = picked;
      if (endDate != null && picked.isAfter(endDate!)) endDate = picked;
    });
  }

  Future<void> pickEndDate() async {
    final initial = endDate ?? (startDate ?? DateTime.now());
    final picked = await showDatePicker(
      context: context,
      initialDate: initial,
      firstDate: DateTime(2020),
      lastDate: DateTime(2100),
    );
    if (picked == null) return;

    setState(() {
      endDate = picked;
      if (startDate != null && picked.isBefore(startDate!)) startDate = picked;
    });
  }

  void clearFilters() {
    setState(() {
      teamFilter = 'Todas';
      categoryFilter = 'Todas';
      startDate = null;
      endDate = null;
    });
  }

  Future<void> exportCsv() async {
    final appProvider = Provider.of<AppProvider>(context, listen: false);

    final csv = appProvider.exportReadingsCsv(
      teamFilter: teamFilter,
      categoryFilter: categoryFilter,
      startDate: startDate,
      endDate: endDate,
    );

    try {
      await downloadCsv('leituras_filtradas.csv', csv);

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          backgroundColor: AppColors.green,
          content: const Text('CSV gerado com sucesso'),
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao exportar: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final appProvider = Provider.of<AppProvider>(context);

    final teams = <String>{'Todas', ...appProvider.teams.map((t) => t.name)}.toList();
    final categories = const <String>['Todas', 'Arroz', 'Feijão', 'Outros'];

    return Scaffold(
      appBar: AppBar(
        title: const Text('Exportar Planilhas'),
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
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: DropdownButtonFormField<String>(
                            value: teamFilter,
                            decoration: const InputDecoration(
                              labelText: 'Equipe',
                              border: OutlineInputBorder(),
                            ),
                            items: teams
                                .map((t) => DropdownMenuItem(
                                      value: t,
                                      child: Text(t),
                                    ))
                                .toList(),
                            onChanged: (v) {
                              if (v == null) return;
                              setState(() => teamFilter = v);
                            },
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: DropdownButtonFormField<String>(
                            value: categoryFilter,
                            decoration: const InputDecoration(
                              labelText: 'Categoria',
                              border: OutlineInputBorder(),
                            ),
                            items: categories
                                .map((c) => DropdownMenuItem(
                                      value: c,
                                      child: Text(c),
                                    ))
                                .toList(),
                            onChanged: (v) {
                              if (v == null) return;
                              setState(() => categoryFilter = v);
                            },
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            icon: const Icon(Icons.date_range),
                            label: Text('Data inicial: ${_formatDate(startDate)}'),
                            onPressed: pickStartDate,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: OutlinedButton.icon(
                            icon: const Icon(Icons.date_range),
                            label: Text('Data final: ${_formatDate(endDate)}'),
                            onPressed: pickEndDate,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Align(
                      alignment: Alignment.centerRight,
                      child: TextButton(
                        onPressed: clearFilters,
                        child: const Text('Limpar filtros'),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton.icon(
                style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary),
                icon: const Icon(Icons.download),
                label: const Text('Gerar CSV'),
                onPressed: exportCsv,
              ),
            ),

            const SizedBox(height: 12),

            Text(
              'No Android o arquivo é salvo nos Documentos do app.\nNo Web o download é direto pelo navegador.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey[700]),
            ),
          ],
        ),
      ),
    );
  }
}