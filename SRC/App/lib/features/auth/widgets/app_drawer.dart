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
    final appProvider = Provider.of<AppProvider>(context);

    final name =
        appProvider.name.trim().isEmpty ? 'Usuário' : appProvider.name.trim();
    final email =
        appProvider.email.trim().isEmpty ? 'sem email' : appProvider.email.trim();
    final roleText = roleLabel(appProvider.userRole);
    final teamText = appProvider.activeTeam?.name ?? 'Nenhuma equipe';

    return Drawer(
      child: Column(
        children: [
          // ===== MINI PERFIL =====
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
                      Text(
                        name,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 2),
                      Text(
                        email,
                        style: const TextStyle(color: Colors.white70),
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 6),
                      Text(
                        roleText,
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Equipe: $teamText',
                        style: const TextStyle(color: Colors.white70),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          const Divider(),

          // ===== EDITAR PERFIL =====
          ListTile(
            leading: const Icon(Icons.edit),
            title: const Text('Editar Perfil'),
            onTap: () => _go(context, AppRoutes.editProfile),
          ),

          const Spacer(),
          const Divider(),

          // ===== LOGOUT =====
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