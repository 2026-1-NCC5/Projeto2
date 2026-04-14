import 'package:flutter/material.dart';

import '../../features/auth/pages/login_page.dart';
import '../../features/auth/pages/register_page.dart';
import '../../features/auth/pages/edit_profile_page.dart';

import '../../features/auth/pages/home_page.dart';
import '../../features/auth/pages/coordinator_home_page.dart';
import '../../features/auth/pages/admin_home_page.dart';

import '../../features/auth/pages/food_register_page.dart';
import '../../features/auth/pages/team_page.dart';
import '../../features/auth/pages/readings_page.dart';
import '../../features/auth/pages/goals_page.dart';

import '../../features/auth/pages/coordinator_dashboard_page.dart';
import '../../features/auth/pages/admin_dashboard_page.dart';
import '../../features/auth/pages/data_table_page.dart';
import '../../features/auth/pages/export_page.dart';
import '../../features/auth/pages/manage_teams_page.dart';

import '../../features/auth/pages/manage_goals_page.dart';
import '../../features/auth/pages/manage_users_page.dart';

class AppRoutes {
  static const login = '/login';
  static const register = '/register';
  static const editProfile = '/profile/edit';

  static const homeOperador = '/home/operador';
  static const homeCoordenador = '/home/coordenador';
  static const homeAdmin = '/home/admin';

  static const foodRegister = '/register-food';
  static const team = '/team';
  static const readings = '/readings';
  static const goals = '/goals';

  static const coordinatorDashboard = '/dashboard/coord';
  static const adminDashboard = '/dashboard/admin';
  static const dataTable = '/data-table';
  static const export = '/export';
  static const manageTeams = '/manage-teams';

  static const manageGoals = '/admin/manage-goals';
  static const manageUsers = '/admin/manage-users';
}

final Map<String, WidgetBuilder> appRoutes = {
  AppRoutes.login: (_) => const LoginPage(),
  AppRoutes.register: (_) => const RegisterPage(),
  AppRoutes.editProfile: (_) => const EditProfilePage(),

  AppRoutes.homeOperador: (_) => const HomePage(),
  AppRoutes.homeCoordenador: (_) => const CoordinatorHomePage(),
  AppRoutes.homeAdmin: (_) => const AdminHomePage(),

  AppRoutes.foodRegister: (_) => const FoodRegisterPage(),
  AppRoutes.team: (_) => const TeamPage(),
  AppRoutes.readings: (_) => const ReadingsPage(),
  AppRoutes.goals: (_) => const GoalsPage(),

  AppRoutes.coordinatorDashboard: (_) => const CoordinatorDashboardPage(),
  AppRoutes.adminDashboard: (_) => const AdminDashboardPage(),
  AppRoutes.dataTable: (_) => const DataTablePage(),
  AppRoutes.export: (_) => const ExportPage(),
  AppRoutes.manageTeams: (_) => const ManageTeamsPage(),

  AppRoutes.manageGoals: (_) => const ManageGoalsPage(),
  AppRoutes.manageUsers: (_) => const ManageUsersPage(),
};
