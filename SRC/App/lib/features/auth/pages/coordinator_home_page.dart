import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/providers/app_provider.dart';
import '../../../core/routes/app_routes.dart';
import '../../../core/theme/app_colors.dart';
import '../widgets/app_drawer.dart';

class CoordinatorHomePage extends StatelessWidget {
  const CoordinatorHomePage({super.key});

  @override
  Widget build(BuildContext context) {
    final p = Provider.of<AppProvider>(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Home — Coordenador'), centerTitle: true),
      drawer: const AppDrawer(),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Card(
              child: ListTile(
                leading: Icon(Icons.supervisor_account, color: AppColors.primary),
                title: Text(p.name.isEmpty ? 'Coordenador' : p.name),
                subtitle: Text('Equipe: ${p.activeTeam?.name ?? "Nenhuma"}'),
              ),
            ),
            const SizedBox(height: 12),
            Card(
              child: ListTile(
                leading: Icon(Icons.set_meal, size: 30, color: AppColors.primary),
                title: const Text('Registrar Alimentos'),
                subtitle: const Text('Informe os quilos coletados'),
                onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.foodRegister),
              ),
            ),
            Card(
              child: ListTile(
                leading: const Icon(Icons.bar_chart, size: 30),
                title: const Text('Dashboard da Equipe'),
                subtitle: const Text('Progresso e metas da equipe'),
                onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.coordinatorDashboard),
              ),
            ),
            Card(
              child: ListTile(
                leading: const Icon(Icons.history, size: 30),
                title: const Text('Leituras'),
                subtitle: const Text('Ver registros enviados'),
                onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.readings),
              ),
            ),
            Card(
              child: ListTile(
                leading: const Icon(Icons.download, size: 30),
                title: const Text('Exportar'),
                subtitle: const Text('Gerar CSV da equipe'),
                onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.export),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
