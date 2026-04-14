import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/goals_api.dart';
import '../../../core/providers/app_provider.dart';
import '../../../core/routes/app_routes.dart';
import '../../../core/theme/app_colors.dart';

class ManageGoalsPage extends StatefulWidget {
  const ManageGoalsPage({super.key});

  @override
  State<ManageGoalsPage> createState() => _ManageGoalsPageState();
}

class _ManageGoalsPageState extends State<ManageGoalsPage> {
  TeamLite? _selectedTeam;
  FoodCategory _selectedCategory = FoodCategory.arroz;
  final _targetController = TextEditingController();

  bool _loading = false;
  List<GoalItem> _goals = [];

  @override
  void initState() {
    super.initState();
    _loadGoals();
  }

  @override
  void dispose() {
    _targetController.dispose();
    super.dispose();
  }

  GoalsApi _api(BuildContext context) {
    final p = Provider.of<AppProvider>(context, listen: false);
    return GoalsApi(ApiClient()..setToken(p.token));
  }

  Future<void> _loadGoals() async {
    setState(() => _loading = true);
    try {
      final data = await _api(context).getGoals();
      if (mounted) setState(() => _goals = data.map(GoalItem.fromMap).toList());
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erro: $e')));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _saveGoal() async {
    final team = _selectedTeam;
    if (team == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Selecione uma equipe')));
      return;
    }
    final target = double.tryParse(_targetController.text.trim().replaceAll(',', '.'));
    if (target == null || target <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Informe um valor válido para a meta')));
      return;
    }

    setState(() => _loading = true);
    try {
      await _api(context).upsertGoal(
        teamId: team.id,
        category: foodCategoryToString(_selectedCategory),
        targetKg: target,
      );
      _targetController.clear();
      await _loadGoals();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(backgroundColor: AppColors.green, content: Text('Meta salva com sucesso')),
        );
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erro: $e')));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _deleteGoal(int goalId) async {
    setState(() => _loading = true);
    try {
      await _api(context).deleteGoal(goalId);
      await _loadGoals();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(backgroundColor: AppColors.green, content: Text('Meta removida')),
        );
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erro: $e')));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final p = Provider.of<AppProvider>(context);

    if (_selectedTeam == null && p.teams.isNotEmpty) {
      _selectedTeam = p.teams.first;
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Gerenciar Metas'),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pushReplacementNamed(context, p.homeRoute),
        ),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loadGoals),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    DropdownButtonFormField<TeamLite>(
                      value: _selectedTeam,
                      decoration: const InputDecoration(labelText: 'Equipe', border: OutlineInputBorder()),
                      items: p.teams.map((t) => DropdownMenuItem(value: t, child: Text(t.name))).toList(),
                      onChanged: (v) => setState(() => _selectedTeam = v),
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<FoodCategory>(
                      value: _selectedCategory,
                      decoration: const InputDecoration(labelText: 'Categoria', border: OutlineInputBorder()),
                      items: FoodCategory.values
                          .map((c) => DropdownMenuItem(value: c, child: Text(foodCategoryLabel(c))))
                          .toList(),
                      onChanged: (v) { if (v != null) setState(() => _selectedCategory = v); },
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _targetController,
                      keyboardType: const TextInputType.numberWithOptions(decimal: true),
                      decoration: const InputDecoration(
                        labelText: 'Meta (kg)',
                        suffixText: 'kg',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 12),
                    SizedBox(
                      width: double.infinity,
                      height: 48,
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary),
                        onPressed: _loading ? null : _saveGoal,
                        child: const Text('Salvar meta', style: TextStyle(color: Colors.white)),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: _loading
                  ? const Center(child: CircularProgressIndicator())
                  : _goals.isEmpty
                      ? const Center(child: Text('Nenhuma meta cadastrada'))
                      : ListView.separated(
                          itemCount: _goals.length,
                          separatorBuilder: (_, __) => const SizedBox(height: 8),
                          itemBuilder: (context, i) {
                            final g = _goals[i];
                            return Card(
                              child: ListTile(
                                leading: Icon(Icons.flag, color: AppColors.primary),
                                title: Text('${g.teamName ?? "Equipe ${g.teamId}"} • ${foodCategoryLabel(g.category)}'),
                                subtitle: Text('Meta: ${g.targetKg.toStringAsFixed(1)} kg'),
                                trailing: IconButton(
                                  icon: const Icon(Icons.delete, color: Colors.red),
                                  onPressed: () => _deleteGoal(g.id),
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
