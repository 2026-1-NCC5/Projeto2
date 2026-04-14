import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/readings_api.dart';
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

  List<ReadingEvent> _readings = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadReadings();
  }

  Future<void> _loadReadings() async {
    setState(() => _loading = true);
    final p = Provider.of<AppProvider>(context, listen: false);
    final client = ApiClient()..setToken(p.token);
    try {
      final data = await ReadingsApi(client).getReadings();
      if (mounted) {
        setState(() => _readings = data.map(ReadingEvent.fromMap).toList());
        p.setReadings(data);
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erro: $e')));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> pickStartDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: startDate ?? DateTime.now(),
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
    final picked = await showDatePicker(
      context: context,
      initialDate: endDate ?? (startDate ?? DateTime.now()),
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

  String _formatDate(DateTime? d) {
    if (d == null) return '—';
    return '${d.day.toString().padLeft(2, '0')}/${d.month.toString().padLeft(2, '0')}/${d.year}';
  }

  @override
  Widget build(BuildContext context) {
    final appProvider = Provider.of<AppProvider>(context);
    final teams = <String>{'Todas', ...appProvider.teams.map((t) => t.name)}.toList();
    const categories = <String>['Todas', 'Arroz', 'Feijão', 'Macarrão', 'Açúcar', 'Outros'];

    final filtered = _readings.where((r) {
      final okTeam = teamFilter == 'Todas' || r.teamName == teamFilter;
      final label = foodCategoryLabel(r.category);
      final okCategory = categoryFilter == 'Todas' || label == categoryFilter;
      bool okDate = true;
      if (startDate != null) {
        okDate = okDate && !r.timestamp.isBefore(DateTime(startDate!.year, startDate!.month, startDate!.day));
      }
      if (endDate != null) {
        okDate = okDate && !r.timestamp.isAfter(DateTime(endDate!.year, endDate!.month, endDate!.day, 23, 59, 59));
      }
      return okTeam && okCategory && okDate;
    }).toList();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Tabela de Dados'),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pushReplacementNamed(context, appProvider.homeRoute),
        ),
        actions: [IconButton(icon: const Icon(Icons.refresh), onPressed: _loadReadings)],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : Padding(
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
                                  decoration: const InputDecoration(labelText: 'Equipe', border: OutlineInputBorder()),
                                  items: teams.map((t) => DropdownMenuItem(value: t, child: Text(t))).toList(),
                                  onChanged: (v) { if (v != null) setState(() => teamFilter = v); },
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: DropdownButtonFormField<String>(
                                  value: categoryFilter,
                                  decoration: const InputDecoration(labelText: 'Categoria', border: OutlineInputBorder()),
                                  items: categories.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
                                  onChanged: (v) { if (v != null) setState(() => categoryFilter = v); },
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
                                  label: Text('Início: ${_formatDate(startDate)}'),
                                  onPressed: pickStartDate,
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: OutlinedButton.icon(
                                  icon: const Icon(Icons.date_range),
                                  label: Text('Fim: ${_formatDate(endDate)}'),
                                  onPressed: pickEndDate,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),
                          Row(
                            children: [
                              Expanded(
                                child: Text('Registros: ${filtered.length}',
                                    style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold)),
                              ),
                              TextButton(onPressed: clearFilters, child: const Text('Limpar filtros')),
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
                          DataColumn(label: Text('Kg')),
                          DataColumn(label: Text('Data/Hora')),
                        ],
                        source: _ReadingsDataSource(filtered),
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

  String _fmt(DateTime d) {
    return '${d.day.toString().padLeft(2, '0')}/${d.month.toString().padLeft(2, '0')}/${d.year} ${d.hour.toString().padLeft(2, '0')}:${d.minute.toString().padLeft(2, '0')}';
  }

  @override
  DataRow? getRow(int index) {
    if (index >= rows.length) return null;
    final r = rows[index];
    return DataRow.byIndex(
      index: index,
      cells: [
        DataCell(Text(r.teamName)),
        DataCell(Text(r.userName ?? '—')),
        DataCell(Text(foodCategoryLabel(r.category))),
        DataCell(Text(r.kgAmount.toStringAsFixed(2))),
        DataCell(Text(_fmt(r.timestamp))),
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
