import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/providers/app_provider.dart';
import '../../../core/theme/app_colors.dart';

class DataTablePage extends StatefulWidget {
  const DataTablePage({super.key});

  @override
  State<DataTablePage> createState() => _DataTablePageState();
}

class _DataTablePageState extends State<DataTablePage> {
  String teamFilter = 'Todas';
  String categoryFilter = 'Todas';

  DateTime? startDate;
  DateTime? endDate;

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
      if (endDate != null && picked.isAfter(endDate!)) {
        endDate = picked;
      }
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
      if (startDate != null && picked.isBefore(startDate!)) {
        startDate = picked;
      }
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

  String _formatDate(DateTime? d) {
    if (d == null) return '—';
    return '${d.day.toString().padLeft(2, '0')}/'
        '${d.month.toString().padLeft(2, '0')}/'
        '${d.year}';
  }

  DateTime _startOfDay(DateTime d) => DateTime(d.year, d.month, d.day, 0, 0, 0);
  DateTime _endOfDay(DateTime d) => DateTime(d.year, d.month, d.day, 23, 59, 59);

  @override
  Widget build(BuildContext context) {
    final appProvider = Provider.of<AppProvider>(context);

    final teams = <String>{'Todas', ...appProvider.teams.map((t) => t.name)}.toList();
    final categories = const <String>['Todas', 'Arroz', 'Feijão', 'Outros'];

    final filtered = appProvider.readings.where((r) {
      final okTeam = teamFilter == 'Todas' || r.teamName == teamFilter;

      final label = foodCategoryLabel(r.category);
      final okCategory = categoryFilter == 'Todas' || label == categoryFilter;

      bool okDate = true;
      if (startDate != null) {
        okDate = okDate && !r.timestamp.isBefore(_startOfDay(startDate!));
      }
      if (endDate != null) {
        okDate = okDate && !r.timestamp.isAfter(_endOfDay(endDate!));
      }

      return okTeam && okCategory && okDate;
    }).toList();

    final source = _ReadingsDataSource(filtered);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Tabela de Dados'),
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
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            'Registros: ${filtered.length}',
                            style: TextStyle(
                              color: AppColors.primary,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                        TextButton(
                          onPressed: clearFilters,
                          child: const Text('Limpar filtros'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),
            Expanded(
              child: Card(
                child: PaginatedDataTable(
                  header: const Text('Leituras'),
                  rowsPerPage: 8,
                  columns: const [
                    DataColumn(label: Text('Equipe')),
                    DataColumn(label: Text('Operador')),
                    DataColumn(label: Text('Categoria')),
                    DataColumn(label: Text('Data/Hora')),
                    DataColumn(label: Text('Confiança')),
                  ],
                  source: source,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ReadingsDataSource extends DataTableSource {
  final List<ReadingEvent> rows;
  _ReadingsDataSource(this.rows);

  String _formatDateTime(DateTime d) {
    final dd = d.day.toString().padLeft(2, '0');
    final mm = d.month.toString().padLeft(2, '0');
    final yyyy = d.year.toString();
    final hh = d.hour.toString().padLeft(2, '0');
    final min = d.minute.toString().padLeft(2, '0');
    return '$dd/$mm/$yyyy $hh:$min';
  }

  @override
  DataRow? getRow(int index) {
    if (index >= rows.length) return null;
    final r = rows[index];

    return DataRow.byIndex(
      index: index,
      cells: [
        DataCell(Text(r.teamName)),
        DataCell(Text(r.operatorName)),
        DataCell(Text(foodCategoryLabel(r.category))),
        DataCell(Text(_formatDateTime(r.timestamp))),
        DataCell(Text(r.confidence == null ? '—' : r.confidence!.toStringAsFixed(2))),
      ],
    );
  }

  @override
  bool get isRowCountApproximate => false;

  @override
  int get rowCount => rows.length;

  @override
  int get selectedRowCount => 0;
}