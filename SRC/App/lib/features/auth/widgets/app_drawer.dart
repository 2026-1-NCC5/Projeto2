import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/providers/app_provider.dart';
import '../../../core/routes/app_routes.dart';
import '../../../core/theme/app_colors.dart';

class AppDrawer extends StatelessWidget {
  const AppDrawer({super.key});

  void _go(BuildContext context, String route) {
    Navigator.pop(context);
    Navigator.pushReplacementNamed(context, route);
  }

  @override
  Widget build(BuildContext context) {
    final p = Provider.of<AppProvider>(context);
    final name = p.name.trim().isEmpty ? 'Usuário' : p.name.trim();
    final email = p.email.trim().isEmpty ? 'sem email' : p.email.trim();
    final teamText = p.activeTeam?.name ?? 'Nenhuma equipe';

    return Drawer(
      child: Column(
        children: [
          Container(
            width: double.infinity,
            color: AppColors.primary,
            padding: const EdgeInsets.fromLTRB(16, 48, 16, 16),
            child: Row(
              children: [
                const CircleAvatar(
                  radius: 24,
                  backgroundColor: Colors.white,
                  child: Icon(Icons.person, color: Colors.black),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(name,
                          style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
                          overflow: TextOverflow.ellipsis),
                      Text(email,
                          style: const TextStyle(color: Colors.white70),
                          overflow: TextOverflow.ellipsis),
                      const SizedBox(height: 4),
                      Text(roleLabel(p.userRole),
                          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
                      Text('Equipe: $teamText',
                          style: const TextStyle(color: Colors.white70),
                          overflow: TextOverflow.ellipsis),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const Divider(),

          // ─── Operador ───
          if (p.isOperador) ...[
            ListTile(
              leading: const Icon(Icons.set_meal),
              title: const Text('Registrar Alimentos'),
              onTap: () => _go(context, AppRoutes.foodRegister),
            ),
            ListTile(
              leading: const Icon(Icons.history),
              title: const Text('Leituras'),
              onTap: () => _go(context, AppRoutes.readings),
            ),
          ],

          // ─── Coordenador ───
          if (p.isCoordenador) ...[
            ListTile(
              leading: const Icon(Icons.set_meal),
              title: const Text('Registrar Alimentos'),
              onTap: () => _go(context, AppRoutes.foodRegister),
            ),
            ListTile(
              leading: const Icon(Icons.history),
              title: const Text('Leituras'),
              onTap: () => _go(context, AppRoutes.readings),
            ),
            ListTile(
              leading: const Icon(Icons.bar_chart),
              title: const Text('Dashboard da Equipe'),
              onTap: () => _go(context, AppRoutes.coordinatorDashboard),
            ),
            ListTile(
              leading: const Icon(Icons.download),
              title: const Text('Exportar'),
              onTap: () => _go(context, AppRoutes.export),
            ),
          ],

          // ─── Admin ───
          if (p.isAdmin) ...[
            ListTile(
              leading: const Icon(Icons.dashboard),
              title: const Text('Dashboard Geral'),
              onTap: () => _go(context, AppRoutes.adminDashboard),
            ),
            ListTile(
              leading: const Icon(Icons.people),
              title: const Text('Gerenciar Usuários'),
              onTap: () => _go(context, AppRoutes.manageUsers),
            ),
            ListTile(
              leading: const Icon(Icons.flag),
              title: const Text('Gerenciar Metas'),
              onTap: () => _go(context, AppRoutes.manageGoals),
            ),
            ListTile(
              leading: const Icon(Icons.groups),
              title: const Text('Gerenciar Equipes'),
              onTap: () => _go(context, AppRoutes.manageTeams),
            ),
            ListTile(
              leading: const Icon(Icons.table_chart),
              title: const Text('Tabela de Dados'),
              onTap: () => _go(context, AppRoutes.dataTable),
            ),
            ListTile(
              leading: const Icon(Icons.download),
              title: const Text('Exportar'),
              onTap: () => _go(context, AppRoutes.export),
            ),
          ],

          const Divider(),
          ListTile(
            leading: const Icon(Icons.edit),
            title: const Text('Editar Perfil'),
            onTap: () => _go(context, AppRoutes.editProfile),
          ),
          const Spacer(),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.logout),
            title: const Text('Sair da conta'),
            onTap: () {
              Provider.of<AppProvider>(context, listen: false).logout();
              _go(context, AppRoutes.login);
            },
          ),
        ],
      ),
    );
  }
}
