import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/providers/app_provider.dart';
import '../../../core/routes/app_routes.dart';
import '../widgets/app_drawer.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    final appProvider = Provider.of<AppProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Home - Operador'),
        centerTitle: true,
      ),
      drawer: const AppDrawer(),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Card(
              child: ListTile(
                leading: const Icon(Icons.person),
                title: Text(appProvider.name.isEmpty ? 'Operador' : appProvider.name),
                subtitle: Text('Equipe ativa: ${appProvider.activeTeam?.name ?? "Nenhuma"}'),
                trailing: Chip(label: Text('Leituras: ${appProvider.readings.length}')),
              ),
            ),
            const SizedBox(height: 12),
            Card(
              child: ListTile(
                leading: const Icon(Icons.camera_alt, size: 30),
                title: const Text('Leitura pela Câmera'),
                subtitle: const Text('Registrar arroz, feijão e outros'),
                onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.camera),
              ),
            ),
            Card(
              child: ListTile(
                leading: const Icon(Icons.groups, size: 30),
                title: const Text('Entrar em Equipe'),
                subtitle: const Text('Selecionar equipe para contagem'),
                onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.team),
              ),
            ),
            Card(
              child: ListTile(
                leading: const Icon(Icons.receipt_long, size: 30),
                title: const Text('Dados da Leitura'),
                subtitle: const Text('Visualizar registros'),
                onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.readings),
              ),
            ),
            Card(
              child: ListTile(
                leading: const Icon(Icons.flag, size: 30),
                title: const Text('Metas'),
                subtitle: const Text('Acompanhar progresso'),
                onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.goals),
              ),
            ),
          ],
        ),
      ),
    );
  }
}