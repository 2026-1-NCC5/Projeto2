import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/goals_api.dart';
import '../../../core/api/readings_api.dart';
import '../../../core/providers/app_provider.dart';
import '../../../core/theme/app_colors.dart';

class GoalsPage extends StatefulWidget {
  const GoalsPage({super.key});

  @override
  State<GoalsPage> createState() => _GoalsPageState();
}

class _GoalsPageState extends State<GoalsPage> {
  bool _loading = true;
  List<GoalItem> _goals = [];
  List<ReadingSummary> _summary = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final p = Provider.of<AppProvider>(context, listen: false);
    final client = ApiClient()..setToken(p.token);
    try {
      final goalsData = await GoalsApi(client).getGoals(teamId: p.userTeamId);
      final summaryData = await ReadingsApi(client).getSummary(teamId: p.userTeamId);
      if (mounted) {
        setState(() {
          _goals = goalsData.map(GoalItem.fromMap).toList();
          _summary = summaryData.map(ReadingSummary.fromMap).toList();
        });
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erro: $e')));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  double _collected(FoodCategory cat) =>
      _summary.where((s) => s.category == cat).fold(0.0, (sum, s) => sum + s.totalKg);

  @override
  Widget build(BuildContext context) {
    final appProvider = Provider.of<AppProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Metas'),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pushReplacementNamed(context, appProvider.homeRoute),
        ),
        actions: [IconButton(icon: const Icon(Icons.refresh), onPressed: _load)],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : Padding(
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
                  Expanded(
                    child: _goals.isEmpty
                        ? const Center(child: Text('Nenhuma meta encontrada'))
                        : ListView.separated(
                            itemCount: _goals.length,
                            separatorBuilder: (_, __) => const SizedBox(height: 8),
                            itemBuilder: (context, index) {
                              final g = _goals[index];
                              final current = _collected(g.category);
                              final progress = g.targetKg == 0
                                  ? 0.0
                                  : (current / g.targetKg).clamp(0.0, 1.0);

                              return Card(
                                child: ListTile(
                                  leading: Icon(Icons.flag, color: AppColors.primary),
                                  title: Text('${g.teamName ?? "Equipe"} • ${foodCategoryLabel(g.category)}'),
                                  subtitle: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text('Meta: ${g.targetKg.toStringAsFixed(1)} kg | Atual: ${current.toStringAsFixed(1)} kg'),
                                      const SizedBox(height: 6),
                                      LinearProgressIndicator(
                                        value: progress,
                                        color: AppColors.primary,
                                        backgroundColor: Colors.grey.shade200,
                                      ),
                                    ],
                                  ),
                                  trailing: Text(
                                    '${(progress * 100).toStringAsFixed(0)}%',
                                    style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold),
                                  ),
                                ),
                              );
                            },
                          ),
                  ),
                ],
              ),
            ),
    );
  }
}
