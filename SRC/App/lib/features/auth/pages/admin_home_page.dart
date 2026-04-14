import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/providers/app_provider.dart';
import '../../../core/routes/app_routes.dart';
import '../../../core/theme/app_colors.dart';
import '../widgets/app_drawer.dart';

class AdminHomePage extends StatelessWidget {
  const AdminHomePage({super.key});

  @override
  Widget build(BuildContext context) {
    final p = Provider.of<AppProvider>(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Home — Admin'), centerTitle: true),
      drawer: const AppDrawer(),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Card(
              child: ListTile(
                leading: Icon(Icons.admin_panel_settings, color: AppColors.primary),
                title: Text(p.name.isEmpty ? 'Admin' : p.name),
                subtitle: Text('Equipes: ${p.teams.length}'),
              ),
            ),
            const SizedBox(height: 12),
            Card(
              child: ListTile(
                leading: const Icon(Icons.dashboard, size: 30),
                title: const Text('Dashboard Geral'),
                subtitle: const Text('Resultados de todas as equipes'),
                onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.adminDashboard),
              ),
            ),
            Card(
              child: ListTile(
                leading: const Icon(Icons.people, size: 30),
                title: const Text('Gerenciar Usuários'),
                subtitle: const Text('Criar e editar contas'),
                onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.manageUsers),
              ),
            ),
            Card(
              child: ListTile(
                leading: const Icon(Icons.flag_outlined, size: 30),
                title: const Text('Gerenciar Metas'),
                subtitle: const Text('Metas por equipe e categoria'),
                onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.manageGoals),
              ),
            ),
            Card(
              child: ListTile(
                leading: const Icon(Icons.groups_2, size: 30),
                title: const Text('Gerenciar Equipes'),
                subtitle: const Text('Criar e remover equipes'),
                onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.manageTeams),
              ),
            ),
            Card(
              child: ListTile(
                leading: const Icon(Icons.table_chart, size: 30),
                title: const Text('Tabela de Dados'),
                subtitle: const Text('Visualizar e filtrar leituras'),
                onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.dataTable),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
