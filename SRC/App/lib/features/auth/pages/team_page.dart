import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/providers/app_provider.dart';
import '../../../core/theme/app_colors.dart';

class TeamPage extends StatelessWidget {
  const TeamPage({super.key});

  @override
  Widget build(BuildContext context) {
    final appProvider = Provider.of<AppProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Entrar em Equipe'),
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
                leading: const Icon(Icons.star),
                title: const Text('Equipe ativa'),
                subtitle: Text(appProvider.activeTeam?.name ?? 'Nenhuma'),
              ),
            ),
            const SizedBox(height: 12),

            Expanded(
              child: ListView.separated(
                itemCount: appProvider.teams.length,
                separatorBuilder: (_, __) => const SizedBox(height: 8),
                itemBuilder: (context, index) {
                  final team = appProvider.teams[index];
                  final isActive = appProvider.activeTeam?.name == team.name;

                  return Card(
                    child: ListTile(
                      leading: Icon(isActive ? Icons.check_circle : Icons.groups,
                          color: isActive ? AppColors.green : null),
                      title: Text(team.name),
                      subtitle: Text(isActive ? 'Selecionada' : 'Toque para entrar'),
                      onTap: () {
                        appProvider.setActiveTeam(team);
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            backgroundColor: AppColors.green,
                            content: Text('Equipe ativa: ${team.name}'),
                          ),
                        );
                      },
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