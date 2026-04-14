import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/users_api.dart';
import '../../../core/providers/app_provider.dart';
import '../../../core/routes/app_routes.dart';
import '../../../core/theme/app_colors.dart';

class ManageUsersPage extends StatefulWidget {
  const ManageUsersPage({super.key});

  @override
  State<ManageUsersPage> createState() => _ManageUsersPageState();
}

class _ManageUsersPageState extends State<ManageUsersPage> {
  final nameController = TextEditingController();
  final emailController = TextEditingController();
  final passwordController = TextEditingController();

  String selectedRole = 'operador';
  int? selectedTeamId;
  bool active = true;
  bool loading = false;

  List<Map<String, dynamic>> users = [];

  @override
  void initState() {
    super.initState();
    loadUsers();
  }

  @override
  void dispose() {
    nameController.dispose();
    emailController.dispose();
    passwordController.dispose();
    super.dispose();
  }

  UsersApi _usersApi(BuildContext context) {
    final appProvider = Provider.of<AppProvider>(context, listen: false);
    final client = ApiClient();
    client.setToken(appProvider.token);
    return UsersApi(client);
  }

  Future<void> loadUsers() async {
    setState(() => loading = true);
    try {
      final result = await _usersApi(context).getUsers();
      if (mounted) setState(() => users = result);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erro ao carregar usuários: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> createUser() async {
    if (nameController.text.trim().isEmpty ||
        emailController.text.trim().isEmpty ||
        passwordController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Preencha nome, email e senha')),
      );
      return;
    }
    setState(() => loading = true);
    try {
      await _usersApi(context).createUser(
        name: nameController.text.trim(),
        email: emailController.text.trim(),
        password: passwordController.text.trim(),
        role: selectedRole,
        teamId: selectedTeamId,
        active: active,
      );
      nameController.clear();
      emailController.clear();
      passwordController.clear();
      if (mounted) setState(() { selectedRole = 'operador'; selectedTeamId = null; active = true; });
      await loadUsers();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(backgroundColor: AppColors.green, content: Text('Usuário criado')),
        );
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erro: $e')));
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> deleteUser(int id) async {
    setState(() => loading = true);
    try {
      await _usersApi(context).deleteUser(id);
      await loadUsers();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(backgroundColor: AppColors.green, content: Text('Usuário removido')),
        );
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erro: $e')));
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> toggleActive(Map<String, dynamic> user) async {
    setState(() => loading = true);
    try {
      await _usersApi(context).updateUser(userId: user['id'], active: !(user['active'] as bool));
      await loadUsers();
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erro: $e')));
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Color roleColor(String role) {
    switch (role) {
      case 'admin': return Colors.red;
      case 'coordenador': return Colors.orange;
      default: return Colors.blue;
    }
  }

  @override
  Widget build(BuildContext context) {
    final appProvider = Provider.of<AppProvider>(context, listen: false);
    final teams = appProvider.teams;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Gerenciar Usuários'),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pushReplacementNamed(context, appProvider.homeRoute),
        ),
        actions: [
          IconButton(onPressed: loading ? null : loadUsers, icon: const Icon(Icons.refresh)),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Criar novo usuário', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 12),
                    TextField(controller: nameController, decoration: const InputDecoration(labelText: 'Nome')),
                    const SizedBox(height: 8),
                    TextField(controller: emailController, decoration: const InputDecoration(labelText: 'Email')),
                    const SizedBox(height: 8),
                    TextField(controller: passwordController, obscureText: true, decoration: const InputDecoration(labelText: 'Senha')),
                    const SizedBox(height: 8),
                    DropdownButtonFormField<String>(
                      value: selectedRole,
                      decoration: const InputDecoration(labelText: 'Perfil'),
                      items: const [
                        DropdownMenuItem(value: 'operador', child: Text('Operador')),
                        DropdownMenuItem(value: 'coordenador', child: Text('Coordenador')),
                        DropdownMenuItem(value: 'admin', child: Text('Admin')),
                      ],
                      onChanged: (v) { if (v != null) setState(() => selectedRole = v); },
                    ),
                    const SizedBox(height: 8),
                    DropdownButtonFormField<int?>(
                      value: selectedTeamId,
                      decoration: const InputDecoration(labelText: 'Equipe (opcional)'),
                      items: [
                        const DropdownMenuItem(value: null, child: Text('Sem equipe')),
                        ...teams.map((t) => DropdownMenuItem(value: t.id, child: Text(t.name))),
                      ],
                      onChanged: (v) => setState(() => selectedTeamId = v),
                    ),
                    const SizedBox(height: 8),
                    SwitchListTile(
                      title: const Text('Usuário ativo'),
                      value: active,
                      onChanged: (v) => setState(() => active = v),
                    ),
                    const SizedBox(height: 8),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary),
                        onPressed: loading ? null : createUser,
                        child: const Text('Criar usuário', style: TextStyle(color: Colors.white)),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: loading
                  ? const Center(child: CircularProgressIndicator())
                  : users.isEmpty
                      ? const Center(child: Text('Nenhum usuário'))
                      : ListView.builder(
                          itemCount: users.length,
                          itemBuilder: (context, i) {
                            final u = users[i];
                            final teamName = u['team_name'] ?? '—';
                            return Card(
                              child: ListTile(
                                title: Text(u['name'] ?? ''),
                                subtitle: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(u['email'] ?? ''),
                                    Text('Equipe: $teamName'),
                                    const SizedBox(height: 4),
                                    Row(children: [
                                      Chip(label: Text(u['role'] ?? ''), backgroundColor: roleColor(u['role'] ?? '')),
                                      const SizedBox(width: 8),
                                      Chip(label: Text(u['active'] == true ? 'Ativo' : 'Inativo')),
                                    ]),
                                  ],
                                ),
                                isThreeLine: true,
                                trailing: Wrap(spacing: 8, children: [
                                  IconButton(tooltip: 'Ativar/Inativar', onPressed: () => toggleActive(u), icon: const Icon(Icons.swap_horiz)),
                                  IconButton(tooltip: 'Excluir', onPressed: () => deleteUser(u['id']), icon: const Icon(Icons.delete, color: Colors.red)),
                                ]),
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
