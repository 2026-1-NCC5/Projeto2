import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/readings_api.dart';
import '../../../core/providers/app_provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/export_downloader.dart';

class DataTablePage extends StatefulWidget {
  const DataTablePage({super.key});

  @override
  State<DataTablePage> createState() => _DataTablePageState();
}

class _DataTablePageState extends State<DataTablePage> {
  int? _teamFilter;
  FoodCategory? _categoryFilter;
  DateTime? _startDate;
  DateTime? _endDate;
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
    final teamIdParam = p.isTeamLocked ? p.userTeamId : null;
    try {
      final data = await ReadingsApi(client).getReadings(teamId: teamIdParam);
      if (mounted) {
        setState(() => _readings = data.map(ReadingEvent.fromMap).toList());
        p.setReadings(data);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erro: $e')));
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  List<ReadingEvent> get _filtered => _readings.where((r) {
        final okTeam = _teamFilter == null || r.teamId == _teamFilter;
        final okCat = _categoryFilter == null || r.category == _categoryFilter;
        bool okDate = true;
        if (_startDate != null) {
          okDate = okDate && !r.timestamp.isBefore(
              DateTime(_startDate!.year, _startDate!.month, _startDate!.day));
        }
        if (_endDate != null) {
          okDate = okDate && !r.timestamp.isAfter(
              DateTime(_endDate!.year, _endDate!.month, _endDate!.day, 23, 59, 59));
        }
        return okTeam && okCat && okDate;
      }).toList();

  double get _totalKg => _filtered.fold(0.0, (s, r) => s + r.kgAmount);

  void _clearFilters() => setState(() {
        _teamFilter = null;
        _categoryFilter = null;
        _startDate = null;
        _endDate = null;
      });

  String _fmtDateTime(DateTime d) =>
      '${d.day.toString().padLeft(2, '0')}/${d.month.toString().padLeft(2, '0')}/${d.year} '
      '${d.hour.toString().padLeft(2, '0')}:${d.minute.toString().padLeft(2, '0')}';

  String _fmtDate(DateTime? d) {
    if (d == null) return '—';
    return '${d.day.toString().padLeft(2, '0')}/${d.month.toString().padLeft(2, '0')}/${d.year}';
  }

  Future<void> _pickDate(bool isStart) async {
    final initial = isStart ? (_startDate ?? DateTime.now()) : (_endDate ?? _startDate ?? DateTime.now());
    final picked = await showDatePicker(
      context: context,
      initialDate: initial,
      firstDate: DateTime(2020),
      lastDate: DateTime(2100),
    );
    if (picked == null) return;
    setState(() {
      if (isStart) {
        _startDate = picked;
        if (_endDate != null && picked.isAfter(_endDate!)) _endDate = picked;
      } else {
        _endDate = picked;
        if (_startDate != null && picked.isBefore(_startDate!)) _startDate = picked;
      }
    });
  }

  Future<void> _exportCsv() async {
    final filtered = _filtered;
    final buffer = StringBuffer();
    buffer.writeln('equipe,operador,categoria,kg,data');
    for (final r in filtered) {
      buffer.writeln(
          '${r.teamName},${r.userName ?? ""},${foodCategoryLabel(r.category)},${r.kgAmount},${r.timestamp.toIso8601String()}');
    }
    try {
      await downloadCsv('leituras_filtradas.csv', buffer.toString());
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(backgroundColor: AppColors.green, content: const Text('CSV exportado com sucesso')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erro ao exportar: $e')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final p = Provider.of<AppProvider>(context);
    final isWide = MediaQuery.of(context).size.width > 640;
    final filtered = _filtered;

    return Scaffold(
      backgroundColor: Colors.grey[100],
      appBar: AppBar(
        title: const Text('Tabela de Dados'),
        centerTitle: true,
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pushReplacementNamed(context, p.homeRoute),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.download),
            tooltip: 'Exportar CSV',
            onPressed: _loading ? null : _exportCsv,
          ),
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loadReadings),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _buildFilters(p, isWide),
                _buildStatsBar(filtered),
                Expanded(
                  child: filtered.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.search_off, size: 48, color: Colors.grey[400]),
                              const SizedBox(height: 8),
                              Text('Nenhum registro encontrado',
                                  style: TextStyle(color: Colors.grey[600])),
                            ],
                          ),
                        )
                      : isWide
                          ? _buildWideTable(filtered)
                          : _buildNarrowList(filtered),
                ),
              ],
            ),
    );
  }

  Widget _buildFilters(AppProvider p, bool isWide) {
    final hasFilters = _teamFilter != null || _categoryFilter != null ||
        _startDate != null || _endDate != null;

    return Container(
      color: Colors.white,
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (p.isAdmin) ...[
            DropdownButtonFormField<int?>(
              value: _teamFilter,
              decoration: InputDecoration(
                labelText: 'Equipe',
                prefixIcon: const Icon(Icons.groups),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                isDense: true,
              ),
              items: [
                const DropdownMenuItem(value: null, child: Text('Todas as equipes')),
                ...p.teams.map((t) => DropdownMenuItem(value: t.id, child: Text(t.name))),
              ],
              onChanged: (v) => setState(() => _teamFilter = v),
            ),
            const SizedBox(height: 10),
          ],
          const Text('Categoria', style: TextStyle(fontSize: 12, color: Colors.black54)),
          const SizedBox(height: 6),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _categoryChip(null, 'Todas'),
                ...FoodCategory.values
                    .map((c) => _categoryChip(c, foodCategoryLabel(c))),
              ],
            ),
          ),
          const SizedBox(height: 10),
          isWide
              ? Row(children: [
                  Expanded(child: _dateButton(true)),
                  const SizedBox(width: 10),
                  Expanded(child: _dateButton(false)),
                  if (hasFilters) ...[
                    const SizedBox(width: 10),
                    TextButton.icon(
                      icon: const Icon(Icons.clear, size: 16),
                      label: const Text('Limpar'),
                      onPressed: _clearFilters,
                    ),
                  ],
                ])
              : Column(children: [
                  Row(children: [
                    Expanded(child: _dateButton(true)),
                    const SizedBox(width: 10),
                    Expanded(child: _dateButton(false)),
                  ]),
                  if (hasFilters)
                    Align(
                      alignment: Alignment.centerRight,
                      child: TextButton.icon(
                        icon: const Icon(Icons.clear, size: 16),
                        label: const Text('Limpar filtros'),
                        onPressed: _clearFilters,
                      ),
                    ),
                ]),
        ],
      ),
    );
  }

  Widget _categoryChip(FoodCategory? cat, String label) {
    final selected = _categoryFilter == cat;
    return Padding(
      padding: const EdgeInsets.only(right: 6),
      child: FilterChip(
        label: Text(label),
        selected: selected,
        selectedColor: AppColors.primary.withOpacity(0.15),
        checkmarkColor: AppColors.primary,
        labelStyle: TextStyle(
          color: selected ? AppColors.primary : Colors.black87,
          fontWeight: selected ? FontWeight.bold : FontWeight.normal,
          fontSize: 13,
        ),
        side: BorderSide(color: selected ? AppColors.primary : Colors.grey.shade300),
        onSelected: (_) => setState(() => _categoryFilter = cat),
      ),
    );
  }

  Widget _dateButton(bool isStart) {
    final date = isStart ? _startDate : _endDate;
    final hasDate = date != null;
    return OutlinedButton.icon(
      style: OutlinedButton.styleFrom(
        foregroundColor: hasDate ? AppColors.primary : Colors.black54,
        side: BorderSide(color: hasDate ? AppColors.primary : Colors.grey.shade300),
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
      ),
      icon: const Icon(Icons.calendar_today, size: 16),
      label: Text(
        isStart ? 'Início: ${_fmtDate(_startDate)}' : 'Fim: ${_fmtDate(_endDate)}',
        style: const TextStyle(fontSize: 13),
        overflow: TextOverflow.ellipsis,
      ),
      onPressed: () => _pickDate(isStart),
    );
  }

  Widget _buildStatsBar(List<ReadingEvent> filtered) {
    return Container(
      color: AppColors.primary.withOpacity(0.07),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: [
          _statBadge(Icons.list_alt, '${filtered.length} registros'),
          const SizedBox(width: 20),
          _statBadge(Icons.scale, '${_totalKg.toStringAsFixed(1)} kg total'),
        ],
      ),
    );
  }

  Widget _statBadge(IconData icon, String label) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 16, color: AppColors.primary),
        const SizedBox(width: 5),
        Text(label,
            style: TextStyle(
                color: AppColors.primary,
                fontWeight: FontWeight.bold,
                fontSize: 13)),
      ],
    );
  }

  Widget _buildWideTable(List<ReadingEvent> filtered) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Card(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        elevation: 1,
        child: PaginatedDataTable(
          rowsPerPage: 10,
          showFirstLastButtons: true,
          columns: [
            DataColumn(label: Text('Equipe', style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold))),
            DataColumn(label: Text('Operador', style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold))),
            DataColumn(label: Text('Categoria', style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold))),
            DataColumn(label: Text('Kg', style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold)), numeric: true),
            DataColumn(label: Text('Data/Hora', style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold))),
          ],
          source: _ReadingsDataSource(filtered, _fmtDateTime),
        ),
      ),
    );
  }

  Widget _buildNarrowList(List<ReadingEvent> filtered) {
    return ListView.separated(
      padding: const EdgeInsets.all(12),
      itemCount: filtered.length,
      separatorBuilder: (_, __) => const SizedBox(height: 8),
      itemBuilder: (_, i) {
        final r = filtered[i];
        return Card(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          elevation: 1,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(9),
                  decoration: BoxDecoration(
                    color: AppColors.primary.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(_categoryIcon(r.category), color: AppColors.primary, size: 20),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        foodCategoryLabel(r.category),
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '${r.teamName} • ${r.userName ?? "—"}',
                        style: TextStyle(color: Colors.grey[600], fontSize: 12),
                      ),
                      Text(
                        _fmtDateTime(r.timestamp),
                        style: TextStyle(color: Colors.grey[500], fontSize: 11),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: AppColors.primary.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    '${r.kgAmount.toStringAsFixed(1)} kg',
                    style: TextStyle(
                        color: AppColors.primary,
                        fontWeight: FontWeight.bold,
                        fontSize: 13),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  IconData _categoryIcon(FoodCategory cat) {
    switch (cat) {
      case FoodCategory.arroz:
        return Icons.grain;
      case FoodCategory.feijao:
        return Icons.spa;
      case FoodCategory.macarrao:
        return Icons.ramen_dining;
      case FoodCategory.acucar:
        return Icons.icecream;
      case FoodCategory.outros:
        return Icons.inventory_2;
    }
  }
}

class _ReadingsDataSource extends DataTableSource {
  final List<ReadingEvent> rows;
  final String Function(DateTime) fmt;
  _ReadingsDataSource(this.rows, this.fmt);

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
        DataCell(Text(fmt(r.timestamp))),
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
