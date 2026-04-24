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
  bool _showForm = false;
  TeamLite? _filterTeam; // filtro da lista — null = todas

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
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Selecione uma equipe')));
      return;
    }
    final target =
        double.tryParse(_targetController.text.trim().replaceAll(',', '.'));
    if (target == null || target <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Informe um valor válido para a meta')));
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
      if (mounted) setState(() => _showForm = false);
      await _loadGoals();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
              backgroundColor: AppColors.green,
              content: Text('Meta salva com sucesso')),
        );
      }
    } catch (e) {
      if (mounted)
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erro: $e')));
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
          const SnackBar(
              backgroundColor: AppColors.green, content: Text('Meta removida')),
        );
      }
    } catch (e) {
      if (mounted)
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erro: $e')));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  List<GoalItem> get _filteredGoals {
    if (_filterTeam == null) return _goals;
    return _goals.where((g) => g.teamId == _filterTeam!.id).toList();
  }

  @override
  Widget build(BuildContext context) {
    final p = Provider.of<AppProvider>(context);

    if (_selectedTeam == null && p.teams.isNotEmpty) {
      _selectedTeam = p.teams.first;
    }

    final displayed = _filteredGoals;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Gerenciar Metas'),
        centerTitle: true,
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
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
            // ─── Botão / Formulário colapsável ───
            AnimatedCrossFade(
              duration: const Duration(milliseconds: 250),
              crossFadeState:
                  _showForm ? CrossFadeState.showSecond : CrossFadeState.showFirst,
              firstChild: SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10)),
                  ),
                  icon: const Icon(Icons.flag_outlined, color: Colors.white),
                  label: const Text('Criar nova meta',
                      style: TextStyle(color: Colors.white, fontSize: 15)),
                  onPressed: () => setState(() => _showForm = true),
                ),
              ),
              secondChild: Card(
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12)),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('Nova meta',
                              style: TextStyle(
                                  fontSize: 16, fontWeight: FontWeight.bold)),
                          IconButton(
                            icon: const Icon(Icons.close),
                            onPressed: () => setState(() => _showForm = false),
                            visualDensity: VisualDensity.compact,
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      DropdownButtonFormField<TeamLite>(
                        value: _selectedTeam,
                        decoration: const InputDecoration(
                            labelText: 'Equipe', border: OutlineInputBorder()),
                        items: p.teams
                            .map((t) =>
                                DropdownMenuItem(value: t, child: Text(t.name)))
                            .toList(),
                        onChanged: (v) => setState(() => _selectedTeam = v),
                      ),
                      const SizedBox(height: 12),
                      DropdownButtonFormField<FoodCategory>(
                        value: _selectedCategory,
                        decoration: const InputDecoration(
                            labelText: 'Categoria',
                            border: OutlineInputBorder()),
                        items: FoodCategory.values
                            .map((c) => DropdownMenuItem(
                                value: c, child: Text(foodCategoryLabel(c))))
                            .toList(),
                        onChanged: (v) {
                          if (v != null) setState(() => _selectedCategory = v);
                        },
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _targetController,
                        keyboardType: const TextInputType.numberWithOptions(
                            decimal: true),
                        decoration: const InputDecoration(
                          labelText: 'Meta (kg)',
                          suffixText: 'kg',
                          border: OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 12),
                      SizedBox(
                        width: double.infinity,
                        height: 46,
                        child: ElevatedButton(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.primary,
                            shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(8)),
                          ),
                          onPressed: _loading ? null : _saveGoal,
                          child: const Text('Salvar meta',
                              style: TextStyle(color: Colors.white)),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 12),

            // ─── Filtro da lista por equipe ───
            Card(
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10)),
              child: Padding(
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                child: DropdownButtonFormField<TeamLite?>(
                  value: _filterTeam,
                  decoration: const InputDecoration(
                    labelText: 'Filtrar por equipe',
                    border: InputBorder.none,
                    prefixIcon: Icon(Icons.filter_list),
                    isDense: true,
                  ),
                  items: [
                    const DropdownMenuItem(
                        value: null, child: Text('Todas as equipes')),
                    ...p.teams.map((t) =>
                        DropdownMenuItem(value: t, child: Text(t.name))),
                  ],
                  onChanged: (v) => setState(() => _filterTeam = v),
                ),
              ),
            ),
            const SizedBox(height: 8),

            // ─── Lista de metas ───
            Expanded(
              child: _loading
                  ? const Center(child: CircularProgressIndicator())
                  : displayed.isEmpty
                      ? const Center(child: Text('Nenhuma meta cadastrada'))
                      : ListView.separated(
                          itemCount: displayed.length,
                          separatorBuilder: (_, __) =>
                              const SizedBox(height: 8),
                          itemBuilder: (context, i) {
                            final g = displayed[i];
                            return Card(
                              shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(10)),
                              child: ListTile(
                                leading: Icon(Icons.flag,
                                    color: AppColors.primary),
                                title: Text(
                                    '${g.teamName ?? "Equipe ${g.teamId}"} • ${foodCategoryLabel(g.category)}'),
                                subtitle: Text(
                                    'Meta: ${g.targetKg.toStringAsFixed(1)} kg'),
                                trailing: IconButton(
                                  icon: const Icon(Icons.delete,
                                      color: Colors.red),
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
