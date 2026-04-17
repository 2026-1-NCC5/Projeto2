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
  TeamLite? _selectedTeam; // admin only — null = todas as equipes

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final p = Provider.of<AppProvider>(context, listen: false);
    final client = ApiClient()..setToken(p.token);
    final teamId = p.isAdmin ? _selectedTeam?.id : p.userTeamId;
    try {
      final goalsData = await GoalsApi(client).getGoals(teamId: teamId);
      final summaryData = await ReadingsApi(client).getSummary(teamId: teamId);
      if (mounted) {
        setState(() {
          _goals = goalsData.map(GoalItem.fromMap).toList();
          _summary = summaryData.map(ReadingSummary.fromMap).toList();
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erro: $e')));
        setState(() => _loading = false);
      }
    }
  }

  double _collected(GoalItem g) => _summary
      .where((s) => s.category == g.category && s.teamId == g.teamId)
      .fold(0.0, (sum, s) => sum + s.totalKg);

  @override
  Widget build(BuildContext context) {
    final p = Provider.of<AppProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Metas'),
        centerTitle: true,
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pushReplacementNamed(context, p.homeRoute),
        ),
        actions: [IconButton(icon: const Icon(Icons.refresh), onPressed: _load)],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                if (p.isAdmin) _buildTeamFilter(p),
                if (!p.isAdmin)
                  Padding(
                    padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
                    child: Card(
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      child: ListTile(
                        leading: Icon(Icons.groups, color: AppColors.primary),
                        title: const Text('Equipe ativa'),
                        subtitle: Text(p.activeTeam?.name ?? 'Nenhuma'),
                      ),
                    ),
                  ),
                const SizedBox(height: 8),
                Expanded(
                  child: _goals.isEmpty
                      ? const Center(child: Text('Nenhuma meta encontrada'))
                      : ListView.separated(
                          padding: const EdgeInsets.fromLTRB(16, 4, 16, 16),
                          itemCount: _goals.length,
                          separatorBuilder: (_, __) => const SizedBox(height: 8),
                          itemBuilder: (context, index) {
                            final g = _goals[index];
                            final current = _collected(g);
                            final progress = g.targetKg == 0
                                ? 0.0
                                : (current / g.targetKg).clamp(0.0, 1.0);
                            final pct = (progress * 100).toStringAsFixed(0);
                            final Color progressColor = progress >= 1.0
                                ? AppColors.green
                                : progress >= 0.5
                                    ? AppColors.secondary
                                    : AppColors.primary;

                            return Card(
                              shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12)),
                              child: Padding(
                                padding: const EdgeInsets.all(14),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      children: [
                                        Container(
                                          padding: const EdgeInsets.all(6),
                                          decoration: BoxDecoration(
                                            color: AppColors.primary.withOpacity(0.1),
                                            borderRadius: BorderRadius.circular(8),
                                          ),
                                          child: Icon(Icons.flag,
                                              color: AppColors.primary, size: 18),
                                        ),
                                        const SizedBox(width: 10),
                                        Expanded(
                                          child: Column(
                                            crossAxisAlignment:
                                                CrossAxisAlignment.start,
                                            children: [
                                              Text(
                                                foodCategoryLabel(g.category),
                                                style: const TextStyle(
                                                    fontWeight: FontWeight.bold,
                                                    fontSize: 15),
                                              ),
                                              if (p.isAdmin && g.teamName != null)
                                                Text(
                                                  g.teamName!,
                                                  style: TextStyle(
                                                      fontSize: 12,
                                                      color: Colors.grey[600]),
                                                ),
                                            ],
                                          ),
                                        ),
                                        Container(
                                          padding: const EdgeInsets.symmetric(
                                              horizontal: 10, vertical: 4),
                                          decoration: BoxDecoration(
                                            color: progressColor.withOpacity(0.12),
                                            borderRadius: BorderRadius.circular(20),
                                          ),
                                          child: Text(
                                            '$pct%',
                                            style: TextStyle(
                                                color: progressColor,
                                                fontWeight: FontWeight.bold),
                                          ),
                                        ),
                                      ],
                                    ),
                                    const SizedBox(height: 10),
                                    Row(
                                      mainAxisAlignment:
                                          MainAxisAlignment.spaceBetween,
                                      children: [
                                        Text(
                                          '${current.toStringAsFixed(1)} kg coletados',
                                          style: TextStyle(
                                              fontSize: 12, color: Colors.grey[700]),
                                        ),
                                        Text(
                                          'Meta: ${g.targetKg.toStringAsFixed(1)} kg',
                                          style: TextStyle(
                                              fontSize: 12, color: Colors.grey[700]),
                                        ),
                                      ],
                                    ),
                                    const SizedBox(height: 6),
                                    ClipRRect(
                                      borderRadius: BorderRadius.circular(4),
                                      child: LinearProgressIndicator(
                                        value: progress,
                                        color: progressColor,
                                        backgroundColor: Colors.grey.shade200,
                                        minHeight: 8,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
                ),
              ],
            ),
    );
  }

  Widget _buildTeamFilter(AppProvider p) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
      child: Card(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
          child: DropdownButtonFormField<TeamLite?>(
            value: _selectedTeam,
            decoration: const InputDecoration(
              labelText: 'Filtrar por equipe',
              border: InputBorder.none,
              prefixIcon: Icon(Icons.groups),
            ),
            items: [
              const DropdownMenuItem(value: null, child: Text('Todas as equipes')),
              ...p.teams.map((t) => DropdownMenuItem(value: t, child: Text(t.name))),
            ],
            onChanged: (v) {
              setState(() => _selectedTeam = v);
              _load();
            },
          ),
        ),
      ),
    );
  }
}
