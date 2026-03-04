import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/providers/app_provider.dart';
import '../../../core/api/teams_api.dart';
import '../../../core/api/api_client.dart';
import '../../../core/theme/app_colors.dart';

class ManageTeamsPage extends StatefulWidget {
  const ManageTeamsPage({super.key});

  @override
  State<ManageTeamsPage> createState() => _ManageTeamsPageState();
}

class _ManageTeamsPageState extends State<ManageTeamsPage> {
  final teamNameController = TextEditingController();
  final teamsApi = TeamsApi(ApiClient());
  bool loading = false;

  @override
  void initState() {
    super.initState();
    loadTeams();
  }

  @override
  void dispose() {
    teamNameController.dispose();
    super.dispose();
  }

  Future<void> loadTeams() async {
    setState(() => loading = true);
    try {
      final lista = await teamsApi.getTeams();
      if (mounted) {
        Provider.of<AppProvider>(context, listen: false).setTeams(lista);
      }
    } catch (e) {
      debugPrint("Erro ao carregar equipes: $e");
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao carregar equipes: $e')),
      );
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> createTeam() async {
    final name = teamNameController.text.trim();
    if (name.isEmpty) return;

    try {
      await teamsApi.createTeam(name);
      teamNameController.clear();
      await loadTeams();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao criar equipe: $e')),
      );
    }
  }

  Future<void> removeTeam(int id) async {
    try {
      await teamsApi.deleteTeam(id);
      await loadTeams();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao remover equipe: $e')),
      );
    }
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
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : Padding(
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
                    child: ListView.builder(
                      itemCount: appProvider.teams.length,
                      itemBuilder: (context, index) {
                        final team = appProvider.teams[index];
                        return Card(
                          child: ListTile(
                            leading: const Icon(Icons.groups),
                            title: Text(team.name),
                            trailing: IconButton(
                              icon: const Icon(Icons.delete, color: Colors.red),
                              onPressed: () => removeTeam(team.id),
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