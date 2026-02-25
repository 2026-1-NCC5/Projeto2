import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/providers/app_provider.dart';
import '../../../core/theme/app_colors.dart';

class ManageGoalsPage extends StatefulWidget {
  const ManageGoalsPage({super.key});

  @override
  State<ManageGoalsPage> createState() => _ManageGoalsPageState();
}

class _ManageGoalsPageState extends State<ManageGoalsPage> {
  String? selectedTeam;
  FoodCategory selectedCategory = FoodCategory.arroz;

  final targetController = TextEditingController();

  @override
  void dispose() {
    targetController.dispose();
    super.dispose();
  }

  void saveGoal() {
    final appProvider = Provider.of<AppProvider>(context, listen: false);

    final team = selectedTeam;
    if (team == null || team.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Selecione uma equipe')),
      );
      return;
    }

    final target = int.tryParse(targetController.text.trim());
    if (target == null || target <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Informe um número válido para a meta')),
      );
      return;
    }

    appProvider.upsertGoal(
      teamName: team,
      category: selectedCategory,
      target: target,
    );

    targetController.clear();

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: AppColors.green,
        content: const Text('Meta salva com sucesso'),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final appProvider = Provider.of<AppProvider>(context);

    final teams = appProvider.teams.map((t) => t.name).toList();

    // ✅ garante um default sem setState
    if (selectedTeam == null && teams.isNotEmpty) {
      selectedTeam = teams.first;
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Gerenciar Metas'),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pushReplacementNamed(
            context,
            appProvider.homeRoute,
          ),
        ),
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
                    DropdownButtonFormField<String>(
                      value: selectedTeam,
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
                      onChanged: (v) => setState(() => selectedTeam = v),
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<FoodCategory>(
                      value: selectedCategory,
                      decoration: const InputDecoration(
                        labelText: 'Categoria',
                        border: OutlineInputBorder(),
                      ),
                      items: FoodCategory.values
                          .map((c) => DropdownMenuItem(
                                value: c,
                                child: Text(foodCategoryLabel(c)),
                              ))
                          .toList(),
                      onChanged: (v) {
                        if (v == null) return;
                        setState(() => selectedCategory = v);
                      },
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: targetController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: 'Meta (quantidade)',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 12),
                    SizedBox(
                      width: double.infinity,
                      height: 48,
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.primary,
                        ),
                        onPressed: saveGoal,
                        child: const Text('Salvar meta'),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: appProvider.goals.isEmpty
                  ? const Center(child: Text('Nenhuma meta cadastrada'))
                  : ListView.separated(
                      itemCount: appProvider.goals.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 8),
                      itemBuilder: (context, index) {
                        final g = appProvider.goals[index];
                        final current = appProvider.countReadingsFor(
                          teamName: g.teamName,
                          category: g.category,
                        );
                        final progress = g.target == 0
                            ? 0.0
                            : (current / g.target).clamp(0.0, 1.0);

                        return Card(
                          child: ListTile(
                            leading: Icon(Icons.flag, color: AppColors.primary),
                            title: Text('${g.teamName} • ${foodCategoryLabel(g.category)}'),
                            subtitle: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('Meta: ${g.target} | Atual: $current'),
                                const SizedBox(height: 6),
                                LinearProgressIndicator(value: progress),
                              ],
                            ),
                            trailing: IconButton(
                              icon: const Icon(Icons.delete, color: Colors.red),
                              onPressed: () {
                                appProvider.removeGoal(g);
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(content: Text('Meta removida')),
                                );
                              },
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