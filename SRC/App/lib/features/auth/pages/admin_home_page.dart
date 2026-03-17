import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/providers/app_provider.dart';
import '../../../core/routes/app_routes.dart';
import '../widgets/app_drawer.dart';

class AdminHomePage extends StatelessWidget {
  const AdminHomePage({super.key});

  @override
  Widget build(BuildContext context) {
    final appProvider = Provider.of<AppProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Home - Admin'),
        centerTitle: true,
      ),
      drawer: const AppDrawer(),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Card(
              child: ListTile(
                leading: const Icon(Icons.admin_panel_settings),
                title: Text(appProvider.name.isEmpty ? 'Admin' : appProvider.name),
                subtitle: Text('Equipes: ${appProvider.teams.length} | Metas: ${appProvider.goals.length} | Leituras: ${appProvider.readings.length}'),
              ),
            ),
            const SizedBox(height: 12),

            Card(
              child: ListTile(
                leading: const Icon(Icons.person_add, size: 30),
                title: const Text('Criar Usuários / Coordenadores'),
                subtitle: const Text('Gerenciar contas do sistema'),
                onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.manageOperators),
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
                title: const Text('Administrar Equipes'),
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
            Card(
              child: ListTile(
                leading: const Icon(Icons.download, size: 30),
                title: const Text('Exportar Planilhas'),
                subtitle: const Text('Gerar CSV com filtros'),
                onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.export),
              ),
            ),
          ],
        ),
      ),
    );
  }
}