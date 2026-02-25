import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/providers/app_provider.dart';
import '../../../core/routes/app_routes.dart';
import '../widgets/app_drawer.dart';

class CoordinatorHomePage extends StatelessWidget {
  const CoordinatorHomePage({super.key});

  @override
  Widget build(BuildContext context) {
    final appProvider = Provider.of<AppProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Home - Coordenador'),
        centerTitle: true,
      ),
      drawer: const AppDrawer(),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Card(
              child: ListTile(
                leading: const Icon(Icons.supervisor_account),
                title: Text(appProvider.name.isEmpty ? 'Coordenador' : appProvider.name),
                subtitle: Text('Equipes: ${appProvider.teams.length} | Leituras: ${appProvider.readings.length}'),
              ),
            ),
            const SizedBox(height: 12),
            Card(
              child: ListTile(
                leading: const Icon(Icons.table_chart, size: 30),
                title: const Text('Tabela de Dados'),
                subtitle: const Text('Filtros por equipe, categoria e data'),
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
            Card(
              child: ListTile(
                leading: const Icon(Icons.groups_2, size: 30),
                title: const Text('Administrar Equipes'),
                subtitle: const Text('Criar e remover equipes'),
                onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.manageTeams),
              ),
            ),
            const Divider(),
            Card(
              child: ListTile(
                leading: const Icon(Icons.camera_alt, size: 30),
                title: const Text('Leitura pela Câmera'),
                subtitle: const Text('Registrar leituras também'),
                onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.camera),
              ),
            ),
            Card(
              child: ListTile(
                leading: const Icon(Icons.flag, size: 30),
                title: const Text('Metas'),
                subtitle: const Text('Acompanhar metas'),
                onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.goals),
              ),
            ),
          ],
        ),
      ),
    );
  }
}