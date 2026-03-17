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

  factory TeamLite.fromMap(Map<String, dynamic> m) {
    return TeamLite(
      id: (m['id'] as num).toInt(),
      name: (m['name'] ?? '').toString(),
    );
  }
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
  // ===== Perfil/Auth (MVP)
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

  void updateProfileLocal({required String name, required String email}) {
    _name = name.trim();
    _email = email.trim();
    notifyListeners();
  }

  // ===== Equipes (backend/local)
  List<TeamLite> _teams = [];
  TeamLite? _activeTeam;

  List<TeamLite> get teams => List.unmodifiable(_teams);
  TeamLite? get activeTeam => _activeTeam;

  void setTeams(List<Map<String, dynamic>> data) {
    _teams = data.map(TeamLite.fromMap).toList();

    // se a ativa sumiu, limpa
    if (_activeTeam != null && !_teams.any((t) => t.id == _activeTeam!.id)) {
      _activeTeam = null;
    }
    notifyListeners();
  }

  void setActiveTeam(TeamLite? team) {
    _activeTeam = team;
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
    final team = _teams.where((t) => t.name == teamName).toList();
    if (team.isEmpty) return;

    final t = team.first;
    final idx = _goals.indexWhere((g) => g.teamId == t.id && g.category == category);

    final newGoal = Goal(
      teamId: t.id,
      teamName: t.name,
      category: category,
      target: target,
    );

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

  // ===== Export CSV
  String exportReadingsCsv({
    required String teamFilter,
    required String categoryFilter,
    DateTime? startDate,
    DateTime? endDate,
  }) {
    final buffer = StringBuffer();
    buffer.writeln('team,category,operator,timestamp,confidence');

    final filtered = _readings.where((r) {
      final matchTeam = teamFilter == 'Todas' || r.teamName == teamFilter;

      final matchCategory = categoryFilter == 'Todas' ||
          foodCategoryLabel(r.category) == categoryFilter;

      final matchStart = startDate == null ||
          r.timestamp.isAfter(DateTime(startDate.year, startDate.month, startDate.day));

      final matchEnd = endDate == null ||
          r.timestamp.isBefore(DateTime(endDate.year, endDate.month, endDate.day + 1));

      return matchTeam && matchCategory && matchStart && matchEnd;
    });

    for (final r in filtered) {
      buffer.writeln(
        '${r.teamName},'
        '${foodCategoryLabel(r.category)},'
        '${r.operatorName},'
        '${r.timestamp.toIso8601String()},'
        '${r.confidence?.toStringAsFixed(4) ?? ""}',
      );
    }

    return buffer.toString();
  }

  void logout() {
    _userRole = UserRole.operador;
    _name = '';
    _email = '';
    _activeTeam = null;
    notifyListeners();
  }
}