import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/providers/app_provider.dart';
import '../../../core/theme/app_colors.dart';

class GoalsPage extends StatelessWidget {
  const GoalsPage({super.key});

  @override
  Widget build(BuildContext context) {
    final appProvider = Provider.of<AppProvider>(context);

    final activeTeam = appProvider.activeTeam?.name;

    final goalsToShow = activeTeam == null
        ? appProvider.goals
        : appProvider.goals.where((g) => g.teamName == activeTeam).toList();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Metas'),
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
              child: ListTile(
                leading: const Icon(Icons.groups),
                title: const Text('Equipe ativa'),
                subtitle: Text(activeTeam ?? 'Nenhuma'),
              ),
            ),
            const SizedBox(height: 12),
            Expanded(
              child: goalsToShow.isEmpty
                  ? const Center(child: Text('Nenhuma meta encontrada'))
                  : ListView.separated(
                      itemCount: goalsToShow.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 8),
                      itemBuilder: (context, index) {
                        final g = goalsToShow[index];
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
                            trailing: Text(
                              '${(progress * 100).toStringAsFixed(0)}%',
                              style: TextStyle(
                                color: AppColors.primary,
                                fontWeight: FontWeight.bold,
                              ),
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