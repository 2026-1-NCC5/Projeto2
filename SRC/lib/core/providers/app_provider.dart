import 'package:flutter/material.dart';

enum UserRole { operador, coordenador, admin }

String roleLabel(UserRole role) {
  switch (role) {
    case UserRole.admin:
      return 'Admin';
    case UserRole.coordenador:
      return 'Coordenador';
    case UserRole.operador:
      return 'Operador';
  }
}

enum FoodCategory { arroz, feijao, outros }

String foodCategoryLabel(FoodCategory c) {
  switch (c) {
    case FoodCategory.arroz:
      return 'Arroz';
    case FoodCategory.feijao:
      return 'Feijão';
    case FoodCategory.outros:
      return 'Outros';
  }
}

class TeamLite {
  final int id;
  final String name;
  const TeamLite({required this.id, required this.name});
}

class ReadingEvent {
  final int teamId;
  final String teamName;
  final FoodCategory category;
  final DateTime timestamp;
  final String operatorName;
  final double? confidence;

  const ReadingEvent({
    required this.teamId,
    required this.teamName,
    required this.category,
    required this.timestamp,
    required this.operatorName,
    this.confidence,
  });
}

class Goal {
  final int teamId;
  final String teamName;
  final FoodCategory category;
  final int target;

  const Goal({
    required this.teamId,
    required this.teamName,
    required this.category,
    required this.target,
  });
}

class AppProvider extends ChangeNotifier {
  // ===== Perfil / auth (MVP)
  UserRole _userRole = UserRole.operador;
  String _name = '';
  String _email = '';

  UserRole get userRole => _userRole;
  String get name => _name;
  String get email => _email;

  bool get isAdmin => _userRole == UserRole.admin;
  bool get isCoordenador => _userRole == UserRole.coordenador;
  bool get isOperador => _userRole == UserRole.operador;

  String get homeRoute {
    switch (_userRole) {
      case UserRole.admin:
        return '/home/admin';
      case UserRole.coordenador:
        return '/home/coordenador';
      case UserRole.operador:
        return '/home/operador';
    }
  }

  void setUserFromBackend({
    required String name,
    required String email,
    required String role,
  }) {
    _name = name;
    _email = email;

    if (role == 'admin') {
      _userRole = UserRole.admin;
    } else if (role == 'coordenador') {
      _userRole = UserRole.coordenador;
    } else {
      _userRole = UserRole.operador;
    }

    notifyListeners();
  }

  // ===== Equipes (local)
  final List<TeamLite> _teams = [
    const TeamLite(id: 1, name: 'Equipe A'),
    const TeamLite(id: 2, name: 'Equipe B'),
    const TeamLite(id: 3, name: 'Equipe C'),
  ];

  TeamLite? _activeTeam;

  List<TeamLite> get teams => List.unmodifiable(_teams);
  TeamLite? get activeTeam => _activeTeam;

  int _nextTeamId() {
    if (_teams.isEmpty) return 1;
    final maxId = _teams.map((t) => t.id).reduce((a, b) => a > b ? a : b);
    return maxId + 1;
  }

  void setActiveTeam(TeamLite? team) {
    _activeTeam = team;
    notifyListeners();
  }

  void addTeam(String name) {
    final trimmed = name.trim();
    if (trimmed.isEmpty) return;

    final exists = _teams.any((t) => t.name.toLowerCase() == trimmed.toLowerCase());
    if (exists) return;

    _teams.add(TeamLite(id: _nextTeamId(), name: trimmed));
    notifyListeners();
  }

  void removeTeam(TeamLite team) {
    _teams.removeWhere((t) => t.id == team.id);

    if (_activeTeam?.id == team.id) {
      _activeTeam = null;
    }

    _goals.removeWhere((g) => g.teamId == team.id);
    _readings.removeWhere((r) => r.teamId == team.id);

    notifyListeners();
  }

  // ===== Leituras (local)
  final List<ReadingEvent> _readings = [];
  List<ReadingEvent> get readings => List.unmodifiable(_readings);

  void addReading({
    required FoodCategory category,
    double? confidence,
  }) {
    final team = _activeTeam;
    if (team == null) return;

    final operator = _name.trim().isEmpty ? 'Usuário' : _name.trim();

    _readings.insert(
      0,
      ReadingEvent(
        teamId: team.id,
        teamName: team.name,
        category: category,
        timestamp: DateTime.now(),
        operatorName: operator,
        confidence: confidence,
      ),
    );

    notifyListeners();
  }

  int countReadingsFor({
    required String teamName,
    required FoodCategory category,
  }) {
    return _readings.where((r) => r.teamName == teamName && r.category == category).length;
  }

  // ===== Metas (local)
  final List<Goal> _goals = [];
  List<Goal> get goals => List.unmodifiable(_goals);

  void upsertGoal({
    required String teamName,
    required FoodCategory category,
    required int target,
  }) {
    final team = _teams.firstWhere(
      (t) => t.name == teamName,
      orElse: () => const TeamLite(id: -1, name: ''),
    );
    if (team.id == -1) return;

    final idx = _goals.indexWhere((g) => g.teamId == team.id && g.category == category);
    final newGoal = Goal(teamId: team.id, teamName: team.name, category: category, target: target);

    if (idx >= 0) {
      _goals[idx] = newGoal;
    } else {
      _goals.add(newGoal);
    }

    notifyListeners();
  }

  void removeGoal(Goal g) {
    _goals.removeWhere((x) => x.teamId == g.teamId && x.category == g.category);
    notifyListeners();
  }

  void logout() {
    _userRole = UserRole.operador;
    _name = '';
    _email = '';
    _activeTeam = null;
    notifyListeners();
  }
  void updateProfileLocal({required String name, required String email}) {
  _name = name.trim();
  _email = email.trim();
  notifyListeners();
}
String exportReadingsCsv({
  required String teamFilter,
  required String categoryFilter,
  DateTime? startDate,
  DateTime? endDate,
}) {
  final buffer = StringBuffer();
  buffer.writeln('team,category,operator,timestamp');

  final filtered = _readings.where((r) {
    final matchTeam =
        teamFilter == 'Todas' || r.teamName == teamFilter;

    final matchCategory =
        categoryFilter == 'Todas' ||
        foodCategoryLabel(r.category) == categoryFilter;

    final matchStart =
        startDate == null ||
        r.timestamp.isAfter(
          DateTime(startDate.year, startDate.month, startDate.day),
        );

    final matchEnd =
        endDate == null ||
        r.timestamp.isBefore(
          DateTime(endDate.year, endDate.month, endDate.day + 1),
        );

    return matchTeam && matchCategory && matchStart && matchEnd;
  });

  for (final r in filtered) {
    buffer.writeln(
      '${r.teamName},'
      '${foodCategoryLabel(r.category)},'
      '${r.operatorName},'
      '${r.timestamp.toIso8601String()}',
    );
  }

  return buffer.toString();
}
}