import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/goals_api.dart';
import '../../../core/api/readings_api.dart';
import '../../../core/providers/app_provider.dart';
import '../../../core/routes/app_routes.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/export_downloader.dart';

class AdminDashboardPage extends StatefulWidget {
  const AdminDashboardPage({super.key});

  @override
  State<AdminDashboardPage> createState() => _AdminDashboardPageState();
}

class _AdminDashboardPageState extends State<AdminDashboardPage> {
  bool _loading = true;
  String? _error;

  List<ReadingSummary> _allSummary = [];
  List<GoalItem> _allGoals = [];
  TeamLite? _selectedTeam;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() { _loading = true; _error = null; });
    final p = Provider.of<AppProvider>(context, listen: false);
    final client = ApiClient()..setToken(p.token);

    try {
      final summaryData = await ReadingsApi(client).getSummary();
      final goalsData = await GoalsApi(client).getGoals();
      if (!mounted) return;
      setState(() {
        _allSummary = summaryData.map(ReadingSummary.fromMap).toList();
        _allGoals = goalsData.map(GoalItem.fromMap).toList();
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() { _error = e.toString(); _loading = false; });
    }
  }

  List<ReadingSummary> get _filteredSummary {
    if (_selectedTeam == null) return _allSummary;
    return _allSummary.where((s) => s.teamId == _selectedTeam!.id).toList();
  }

  List<GoalItem> get _filteredGoals {
    if (_selectedTeam == null) return _allGoals;
    return _allGoals.where((g) => g.teamId == _selectedTeam!.id).toList();
  }

  double get _totalCollectedAll => _allSummary.fold(0.0, (s, r) => s + r.totalKg);

  double _collected(FoodCategory cat) =>
      _filteredSummary.where((s) => s.category == cat).fold(0.0, (s, r) => s + r.totalKg);

  double _target(FoodCategory cat) {
    final g = _filteredGoals.where((g) => g.category == cat);
    return g.fold(0.0, (s, g) => s + g.targetKg);
  }

  double get _filteredTotal => _filteredSummary.fold(0.0, (s, r) => s + r.totalKg);
  double get _filteredTargetTotal => _filteredGoals.fold(0.0, (s, g) => s + g.targetKg);

  Future<void> _exportDashboard() async {
    final label = _selectedTeam == null ? 'Todas as Equipes' : _selectedTeam!.name;
    final now = DateTime.now();
    final dateStr =
        '${now.day.toString().padLeft(2, '0')}/${now.month.toString().padLeft(2, '0')}/${now.year}';

    final buf = StringBuffer();
    buf.writeln('Dashboard Geral — $label — $dateStr');
    buf.writeln('');
    buf.writeln('categoria,coletado_kg,meta_kg,progresso_%');

    for (final cat in FoodCategory.values) {
      final collected = _collected(cat);
      final target = _target(cat);
      final pct = target > 0 ? (collected / target * 100).toStringAsFixed(1) : '—';
      buf.writeln('${foodCategoryLabel(cat)},${collected.toStringAsFixed(2)},${target > 0 ? target.toStringAsFixed(2) : "—"},$pct');
    }

    buf.writeln('');
    final totalTarget = _filteredTargetTotal;
    final totalPct = totalTarget > 0
        ? (_filteredTotal / totalTarget * 100).toStringAsFixed(1)
        : '—';
    buf.writeln('TOTAL,${_filteredTotal.toStringAsFixed(2)},${totalTarget.toStringAsFixed(2)},$totalPct');

    final fileName = _selectedTeam == null
        ? 'dashboard_geral.csv'
        : 'dashboard_${_selectedTeam!.name.replaceAll(' ', '_')}.csv';

    try {
      await downloadCsv(fileName, buf.toString());
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(backgroundColor: AppColors.green, content: const Text('Dashboard exportado')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erro: $e')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final p = Provider.of<AppProvider>(context);
    final isWide = MediaQuery.of(context).size.width > 600;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard Geral'),
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
            onPressed: _loading ? null : _exportDashboard,
          ),
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loadData),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text('Erro: $_error'))
              : RefreshIndicator(
                  onRefresh: _loadData,
                  child: SingleChildScrollView(
                    physics: const AlwaysScrollableScrollPhysics(),
                    padding: const EdgeInsets.all(16),
                    child: Center(
                      child: ConstrainedBox(
                        constraints: BoxConstraints(maxWidth: isWide ? 800 : double.infinity),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            _buildGlobalCard(),
                            const SizedBox(height: 16),
                            _buildTeamSelector(p),
                            const SizedBox(height: 16),
                            if (_filteredSummary.isNotEmpty || _filteredGoals.isNotEmpty) _buildChart(),
                            const SizedBox(height: 16),
                            ..._buildCategoryCards(isWide),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
    );
  }

  Widget _buildGlobalCard() {
    return Card(
      color: AppColors.primary,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            const Icon(Icons.inventory_2, color: Colors.white, size: 36),
            const SizedBox(width: 16),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Total geral coletado', style: TextStyle(color: Colors.white70, fontSize: 12)),
                Text(
                  '${_totalCollectedAll.toStringAsFixed(1)} kg',
                  style: const TextStyle(color: Colors.white, fontSize: 28, fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTeamSelector(AppProvider p) {
    final teams = p.teams;
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: DropdownButtonFormField<TeamLite?>(
          value: _selectedTeam,
          decoration: const InputDecoration(labelText: 'Filtrar por equipe', border: InputBorder.none),
          items: [
            const DropdownMenuItem(value: null, child: Text('Todas as equipes')),
            ...teams.map((t) => DropdownMenuItem(value: t, child: Text(t.name))),
          ],
          onChanged: (v) => setState(() => _selectedTeam = v),
        ),
      ),
    );
  }

  Widget _buildChart() {
    final categories = FoodCategory.values;
    final groups = categories.asMap().entries.map((e) {
      final cat = e.value;
      final collected = _collected(cat);
      final target = _target(cat);
      return BarChartGroupData(
        x: e.key,
        barRods: [
          BarChartRodData(toY: collected, color: AppColors.primary, width: 14, borderRadius: BorderRadius.circular(4)),
          if (target > 0)
            BarChartRodData(toY: target, color: Colors.grey.shade300, width: 14, borderRadius: BorderRadius.circular(4)),
        ],
        barsSpace: 4,
      );
    }).toList();

    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _selectedTeam == null
                  ? 'Todas as Equipes — Coletado vs Meta (kg)'
                  : '${_selectedTeam!.name} — Coletado vs Meta (kg)',
              style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.primary),
            ),
            const SizedBox(height: 8),
            Row(children: [
              _legend(AppColors.primary, 'Coletado'),
              const SizedBox(width: 16),
              _legend(Colors.grey.shade300, 'Meta'),
            ]),
            const SizedBox(height: 12),
            SizedBox(
              height: 200,
              child: BarChart(
                BarChartData(
                  alignment: BarChartAlignment.spaceAround,
                  barGroups: groups,
                  gridData: const FlGridData(show: false),
                  borderData: FlBorderData(show: false),
                  titlesData: FlTitlesData(
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: (val, _) {
                          final idx = val.toInt();
                          if (idx < 0 || idx >= categories.length) return const SizedBox();
                          return Text(foodCategoryLabel(categories[idx]).substring(0, 2),
                              style: const TextStyle(fontSize: 10));
                        },
                      ),
                    ),
                    leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _legend(Color color, String label) {
    return Row(children: [
      Container(width: 12, height: 12, color: color),
      const SizedBox(width: 4),
      Text(label, style: const TextStyle(fontSize: 12)),
    ]);
  }

  List<Widget> _buildCategoryCards(bool isWide) {
    final cards = FoodCategory.values.map((cat) {
      final collected = _collected(cat);
      final target = _target(cat);
      final progress = target > 0 ? (collected / target).clamp(0.0, 1.0) : 0.0;

      return Card(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
                Text(foodCategoryLabel(cat), style: const TextStyle(fontWeight: FontWeight.bold)),
                Text('${(progress * 100).toStringAsFixed(0)}%',
                    style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold)),
              ]),
              const SizedBox(height: 4),
              Text('${collected.toStringAsFixed(1)} kg / ${target > 0 ? "${target.toStringAsFixed(1)} kg meta" : "sem meta"}',
                  style: const TextStyle(fontSize: 12)),
              const SizedBox(height: 6),
              LinearProgressIndicator(
                value: progress,
                backgroundColor: Colors.grey.shade200,
                color: AppColors.primary,
                minHeight: 6,
              ),
            ],
          ),
        ),
      );
    }).toList();

    if (isWide) {
      final rows = <Widget>[];
      for (var i = 0; i < cards.length; i += 2) {
        rows.add(Row(children: [
          Expanded(child: cards[i]),
          const SizedBox(width: 12),
          Expanded(child: i + 1 < cards.length ? cards[i + 1] : const SizedBox()),
        ]));
        rows.add(const SizedBox(height: 8));
      }
      return rows;
    }
    return cards.map((c) => Padding(padding: const EdgeInsets.only(bottom: 8), child: c)).toList();
  }
}
