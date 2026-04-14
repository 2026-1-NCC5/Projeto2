import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/goals_api.dart';
import '../../../core/api/readings_api.dart';
import '../../../core/providers/app_provider.dart';
import '../../../core/routes/app_routes.dart';
import '../../../core/theme/app_colors.dart';

class CoordinatorDashboardPage extends StatefulWidget {
  const CoordinatorDashboardPage({super.key});

  @override
  State<CoordinatorDashboardPage> createState() => _CoordinatorDashboardPageState();
}

class _CoordinatorDashboardPageState extends State<CoordinatorDashboardPage> {
  bool _loading = true;
  String? _error;

  List<ReadingSummary> _summary = [];
  List<GoalItem> _goals = [];

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() { _loading = true; _error = null; });
    final p = Provider.of<AppProvider>(context, listen: false);
    final client = ApiClient()..setToken(p.token);
    final readingsApi = ReadingsApi(client);
    final goalsApi = GoalsApi(client);

    try {
      final summaryData = await readingsApi.getSummary(teamId: p.userTeamId);
      final goalsData = await goalsApi.getGoals(teamId: p.userTeamId);
      if (!mounted) return;
      setState(() {
        _summary = summaryData.map(ReadingSummary.fromMap).toList();
        _goals = goalsData.map(GoalItem.fromMap).toList();
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() { _error = e.toString(); _loading = false; });
    }
  }

  double _collected(FoodCategory cat) {
    return _summary.where((s) => s.category == cat).fold(0.0, (sum, s) => sum + s.totalKg);
  }

  double _target(FoodCategory cat) {
    final g = _goals.where((g) => g.category == cat);
    return g.isEmpty ? 0.0 : g.first.targetKg;
  }

  double get _totalCollected => _summary.fold(0.0, (s, r) => s + r.totalKg);
  double get _totalTarget => _goals.fold(0.0, (s, g) => s + g.targetKg);

  @override
  Widget build(BuildContext context) {
    final p = Provider.of<AppProvider>(context);
    final isWide = MediaQuery.of(context).size.width > 600;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard da Equipe'),
        centerTitle: true,
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pushReplacementNamed(context, p.homeRoute),
        ),
        actions: [
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
                        constraints: BoxConstraints(maxWidth: isWide ? 720 : double.infinity),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            _buildSummaryCard(),
                            const SizedBox(height: 16),
                            if (_summary.isNotEmpty || _goals.isNotEmpty) _buildChart(),
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

  Widget _buildSummaryCard() {
    final progress = _totalTarget > 0 ? (_totalCollected / _totalTarget).clamp(0.0, 1.0) : 0.0;
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Progresso Geral',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.primary),
            ),
            const SizedBox(height: 8),
            Text(
              '${_totalCollected.toStringAsFixed(1)} kg coletados de ${_totalTarget.toStringAsFixed(1)} kg meta',
              style: const TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 8),
            LinearProgressIndicator(
              value: progress,
              minHeight: 10,
              backgroundColor: Colors.grey.shade200,
              color: AppColors.primary,
            ),
            const SizedBox(height: 4),
            Text('${(progress * 100).toStringAsFixed(1)}%',
                style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold)),
          ],
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
            Text('Coletado vs Meta (kg)',
                style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.primary)),
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
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(foodCategoryLabel(cat), style: const TextStyle(fontWeight: FontWeight.bold)),
                  Text('${(progress * 100).toStringAsFixed(0)}%',
                      style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold)),
                ],
              ),
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
        rows.add(Row(
          children: [
            Expanded(child: cards[i]),
            const SizedBox(width: 12),
            Expanded(child: i + 1 < cards.length ? cards[i + 1] : const SizedBox()),
          ],
        ));
        rows.add(const SizedBox(height: 8));
      }
      return rows;
    }

    return cards.map((c) => Padding(padding: const EdgeInsets.only(bottom: 8), child: c)).toList();
  }
}
