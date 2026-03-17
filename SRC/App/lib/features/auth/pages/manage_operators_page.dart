import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/providers/app_provider.dart';

class ManageOperatorsPage extends StatelessWidget {
  const ManageOperatorsPage({super.key});

  @override
  Widget build(BuildContext context) {
    final appProvider = Provider.of<AppProvider>(context, listen: false);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Usuários / Coordenadores'),
        centerTitle: true,

        // ✅ Voltar sempre para a home do cargo
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
              child: ListTile(
                leading: const Icon(Icons.info_outline),
                title: const Text('Em desenvolvimento (MVP)'),
                subtitle: const Text(
                  'Aqui será o CRUD de usuários, com criação de Operadores e Coordenadores.\n'
                  'No MVP atual, está como placeholder.',
                ),
              ),
            ),
            const SizedBox(height: 12),
            const Expanded(
              child: Center(
                child: Text('CRUD de usuários/perfis (placeholder)'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}