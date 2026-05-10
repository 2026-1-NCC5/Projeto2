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

enum FoodCategory { arroz, feijao, macarrao, acucar, fuba, oleo, outros }

String foodCategoryLabel(FoodCategory c) {
  switch (c) {
    case FoodCategory.arroz:
      return 'Arroz';
    case FoodCategory.feijao:
      return 'Feijão';
    case FoodCategory.macarrao:
      return 'Macarrão';
    case FoodCategory.acucar:
      return 'Açúcar';
    case FoodCategory.fuba:
      return 'Fubá';
    case FoodCategory.oleo:
      return 'Óleo';
    case FoodCategory.outros:
      return 'Outros';
  }
}

FoodCategory? foodCategoryFromString(String s) {
  switch (s) {
    case 'arroz':
      return FoodCategory.arroz;
    case 'feijao':
      return FoodCategory.feijao;
    case 'macarrao':
      return FoodCategory.macarrao;
    case 'acucar':
      return FoodCategory.acucar;
    case 'fuba':
      return FoodCategory.fuba;
    case 'oleo':
      return FoodCategory.oleo;
    case 'outros':
      return FoodCategory.outros;
    default:
      return null;
  }
}

String foodCategoryToString(FoodCategory c) {
  switch (c) {
    case FoodCategory.arroz:
      return 'arroz';
    case FoodCategory.feijao:
      return 'feijao';
    case FoodCategory.macarrao:
      return 'macarrao';
    case FoodCategory.acucar:
      return 'acucar';
    case FoodCategory.fuba:
      return 'fuba';
    case FoodCategory.oleo:
      return 'oleo';
    case FoodCategory.outros:
      return 'outros';
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
  final int id;
  final int teamId;
  final String teamName;
  final int? userId;
  final String? userName;
  final FoodCategory category;
  final double kgAmount;
  final DateTime timestamp;

  const ReadingEvent({
    required this.id,
    required this.teamId,
    required this.teamName,
    this.userId,
    this.userName,
    required this.category,
    required this.kgAmount,
    required this.timestamp,
  });

  factory ReadingEvent.fromMap(Map<String, dynamic> m) {
    return ReadingEvent(
      id: (m['id'] as num).toInt(),
      teamId: (m['team_id'] as num).toInt(),
      teamName: (m['team_name'] ?? '').toString(),
      userId: m['user_id'] != null ? (m['user_id'] as num).toInt() : null,
      userName: m['user_name']?.toString(),
      category: foodCategoryFromString(m['category'] ?? '') ?? FoodCategory.outros,
      kgAmount: (m['kg_amount'] as num?)?.toDouble() ?? 0.0,
      timestamp: DateTime.tryParse(m['created_at'] ?? '') ?? DateTime.now(),
    );
  }
}

class ReadingSummary {
  final int teamId;
  final String teamName;
  final FoodCategory category;
  final double totalKg;

  const ReadingSummary({
    required this.teamId,
    required this.teamName,
    required this.category,
    required this.totalKg,
  });

  factory ReadingSummary.fromMap(Map<String, dynamic> m) {
    return ReadingSummary(
      teamId: (m['team_id'] as num).toInt(),
      teamName: (m['team_name'] ?? '').toString(),
      category: foodCategoryFromString(m['category'] ?? '') ?? FoodCategory.outros,
      totalKg: (m['total_kg'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class GoalItem {
  final int id;
  final int teamId;
  final String? teamName;
  final FoodCategory category;
  final double targetKg;

  const GoalItem({
    required this.id,
    required this.teamId,
    this.teamName,
    required this.category,
    required this.targetKg,
  });

  factory GoalItem.fromMap(Map<String, dynamic> m) {
    return GoalItem(
      id: (m['id'] as num).toInt(),
      teamId: (m['team_id'] as num).toInt(),
      teamName: m['team_name']?.toString(),
      category: foodCategoryFromString(m['category'] ?? '') ?? FoodCategory.outros,
      targetKg: (m['target_kg'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class AppProvider extends ChangeNotifier {
  UserRole _userRole = UserRole.operador;
  int? _userId;
  String _name = '';
  String _email = '';
  String? _token;
  int? _userTeamId;
  String? _userTeamName;

  UserRole get userRole => _userRole;
  int? get userId => _userId;
  String get name => _name;
  String get email => _email;
  String? get token => _token;
  int? get userTeamId => _userTeamId;

  bool get isAdmin => _userRole == UserRole.admin;
  bool get isCoordenador => _userRole == UserRole.coordenador;
  bool get isOperador => _userRole == UserRole.operador;
  bool get isTeamLocked => _userRole != UserRole.admin;

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

  void setToken(String? value) {
    _token = value;
    notifyListeners();
  }

  void setUserFromBackend({
    required int id,
    required String name,
    required String email,
    required String role,
    int? teamId,
    String? teamName,
  }) {
    _userId = id;
    _name = name.trim();
    _email = email.trim();
    _userTeamId = teamId;
    _userTeamName = teamName;

    if (role == 'admin') {
      _userRole = UserRole.admin;
    } else if (role == 'coordenador') {
      _userRole = UserRole.coordenador;
    } else {
      _userRole = UserRole.operador;
    }

    // Lock team for non-admin
    if (teamId != null && teamName != null && _userRole != UserRole.admin) {
      _activeTeam = TeamLite(id: teamId, name: teamName);
    }

    notifyListeners();
  }

  void updateProfileLocal({required String name, required String email}) {
    _name = name.trim();
    _email = email.trim();
    notifyListeners();
  }

  List<TeamLite> _teams = [];
  TeamLite? _activeTeam;

  List<TeamLite> get teams => List.unmodifiable(_teams);
  TeamLite? get activeTeam => _activeTeam;

  void setTeams(List<Map<String, dynamic>> data) {
    _teams = data.map(TeamLite.fromMap).toList();
    if (_activeTeam != null && !_teams.any((t) => t.id == _activeTeam!.id)) {
      if (isTeamLocked) {
        // Keep the locked team even if not in the list
      } else {
        _activeTeam = null;
      }
    }
    notifyListeners();
  }

  void setActiveTeam(TeamLite? team) {
    if (isTeamLocked) return; // Admin-only action
    _activeTeam = team;
    notifyListeners();
  }

  List<ReadingEvent> _readings = [];
  List<ReadingEvent> get readings => List.unmodifiable(_readings);

  void setReadings(List<Map<String, dynamic>> data) {
    _readings = data.map(ReadingEvent.fromMap).toList();
    notifyListeners();
  }

  List<ReadingSummary> _summary = [];
  List<ReadingSummary> get summary => List.unmodifiable(_summary);

  void setSummary(List<Map<String, dynamic>> data) {
    _summary = data.map(ReadingSummary.fromMap).toList();
    notifyListeners();
  }

  List<GoalItem> _goals = [];
  List<GoalItem> get goals => List.unmodifiable(_goals);

  void setGoals(List<Map<String, dynamic>> data) {
    _goals = data.map(GoalItem.fromMap).toList();
    notifyListeners();
  }

  String exportReadingsCsv({
    required String teamFilter,
    required String categoryFilter,
    DateTime? startDate,
    DateTime? endDate,
  }) {
    final buffer = StringBuffer();
    buffer.writeln('equipe,operador,categoria,kg,data');

    final filtered = _readings.where((r) {
      final okTeam = teamFilter == 'Todas' || r.teamName == teamFilter;
      final label = foodCategoryLabel(r.category);
      final okCategory = categoryFilter == 'Todas' || label == categoryFilter;
      bool okDate = true;
      if (startDate != null) {
        okDate = okDate && !r.timestamp.isBefore(DateTime(startDate.year, startDate.month, startDate.day));
      }
      if (endDate != null) {
        okDate = okDate && !r.timestamp.isAfter(DateTime(endDate.year, endDate.month, endDate.day + 1));
      }
      return okTeam && okCategory && okDate;
    });

    for (final r in filtered) {
      buffer.writeln('${r.teamName},${r.userName ?? ""},${foodCategoryLabel(r.category)},${r.kgAmount},${r.timestamp.toIso8601String()}');
    }

    return buffer.toString();
  }

  void logout() {
    _userRole = UserRole.operador;
    _userId = null;
    _name = '';
    _email = '';
    _token = null;
    _activeTeam = null;
    _userTeamId = null;
    _userTeamName = null;
    _readings = [];
    _summary = [];
    _goals = [];
    notifyListeners();
  }
}
