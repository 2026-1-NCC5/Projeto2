import 'package:flutter/material.dart';

// Auth
import '../../features/auth/pages/login_page.dart';
import '../../features/auth/pages/register_page.dart';
import '../../features/auth/pages/edit_profile_page.dart';

// Homes
import '../../features/auth/pages/home_page.dart';
import '../../features/auth/pages/coordinator_home_page.dart';
import '../../features/auth/pages/admin_home_page.dart';

// Operador/Comuns
import '../../features/auth/pages/camera_page.dart';
import '../../features/auth/pages/team_page.dart';
import '../../features/auth/pages/readings_page.dart';
import '../../features/auth/pages/goals_page.dart';

// Coord/Admin
import '../../features/auth/pages/data_table_page.dart';
import '../../features/auth/pages/export_page.dart';
import '../../features/auth/pages/manage_teams_page.dart';

// Admin
import '../../features/auth/pages/manage_goals_page.dart';
import '../../features/auth/pages/manage_operators_page.dart';

class AppRoutes {
  static const splash = '/';

  static const login = '/login';
  static const register = '/register';
  static const editProfile = '/profile/edit';

  // Homes por cargo
  static const homeOperador = '/home/operador';
  static const homeCoordenador = '/home/coordenador';
  static const homeAdmin = '/home/admin';

  // Comuns
  static const camera = '/camera';
  static const team = '/team';
  static const readings = '/readings';
  static const goals = '/goals';

  // Coord/Admin
  static const manageTeams = '/manage-teams';
  static const dataTable = '/data-table';
  static const export = '/export';

  // Admin
  static const manageGoals = '/admin/manage-goals';
  static const manageOperators = '/admin/manage-operators';
}

final Map<String, WidgetBuilder> appRoutes = {
  AppRoutes.login: (_) => const LoginPage(),
  AppRoutes.register: (_) => const RegisterPage(),
  AppRoutes.editProfile: (_) => const EditProfilePage(),

  AppRoutes.homeOperador: (_) => const HomePage(),
  AppRoutes.homeCoordenador: (_) => const CoordinatorHomePage(),
  AppRoutes.homeAdmin: (_) => const AdminHomePage(),

  AppRoutes.camera: (_) => const CameraPage(),
  AppRoutes.team: (_) => const TeamPage(),
  AppRoutes.readings: (_) => const ReadingsPage(),
  AppRoutes.goals: (_) => const GoalsPage(),

  AppRoutes.manageTeams: (_) => const ManageTeamsPage(),
  AppRoutes.dataTable: (_) => const DataTablePage(),
  AppRoutes.export: (_) => const ExportPage(),

  AppRoutes.manageGoals: (_) => const ManageGoalsPage(),
  AppRoutes.manageOperators: (_) => const ManageOperatorsPage(),
};