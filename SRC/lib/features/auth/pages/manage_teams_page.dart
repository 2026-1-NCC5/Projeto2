import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/providers/app_provider.dart';
import '../../../core/theme/app_colors.dart';

class ManageTeamsPage extends StatefulWidget {
  const ManageTeamsPage({super.key});

  @override
  State<ManageTeamsPage> createState() => _ManageTeamsPageState();
}

class _ManageTeamsPageState extends State<ManageTeamsPage> {
  final teamNameController = TextEditingController();

  @override
  void dispose() {
    teamNameController.dispose();
    super.dispose();
  }

  void createTeam() {
    final appProvider = Provider.of<AppProvider>(context, listen: false);
    final name = teamNameController.text.trim();

    if (name.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Informe um nome para a equipe')),
      );
      return;
    }

    // ⚠️ No seu provider atual não tem addTeam (só setTeams vindo do backend).
    // Se você ainda está em MVP local, mantenha addTeam no provider.
    appProvider.addTeam(name);

    teamNameController.clear();

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: AppColors.green,
        content: const Text('Equipe criada com sucesso'),
      ),
    );
  }

  // ✅ aqui está a correção principal: TeamLite
  void removeTeam(TeamLite team) {
    final appProvider = Provider.of<AppProvider>(context, listen: false);
    appProvider.removeTeam(team);

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Equipe removida')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final appProvider = Provider.of<AppProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Administrar Equipes'),
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
                    TextField(
                      controller: teamNameController,
                      decoration: const InputDecoration(
                        labelText: 'Nome da equipe',
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
                        onPressed: createTeam,
                        child: const Text('Criar equipe'),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: ListView.separated(
                itemCount: appProvider.teams.length,
                separatorBuilder: (_, __) => const SizedBox(height: 8),
                itemBuilder: (context, index) {
                  final team = appProvider.teams[index];
                  final isActive = appProvider.activeTeam?.id == team.id;

                  return Card(
                    child: ListTile(
                      leading: Icon(
                        isActive ? Icons.star : Icons.groups,
                        color: isActive ? AppColors.green : null,
                      ),
                      title: Text(team.name),
                      subtitle:
                          Text(isActive ? 'Equipe ativa' : 'Equipe cadastrada'),
                      trailing: IconButton(
                        icon: const Icon(Icons.delete, color: Colors.red),
                        onPressed: () => removeTeam(team),
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