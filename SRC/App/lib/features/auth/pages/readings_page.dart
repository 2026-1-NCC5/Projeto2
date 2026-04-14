import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/readings_api.dart';
import '../../../core/providers/app_provider.dart';
import '../../../core/theme/app_colors.dart';

class ReadingsPage extends StatefulWidget {
  const ReadingsPage({super.key});

  @override
  State<ReadingsPage> createState() => _ReadingsPageState();
}

class _ReadingsPageState extends State<ReadingsPage> {
  bool _loading = true;
  List<ReadingEvent> _readings = [];

  @override
  void initState() {
    super.initState();
    _loadReadings();
  }

  Future<void> _loadReadings() async {
    setState(() => _loading = true);
    final p = Provider.of<AppProvider>(context, listen: false);
    final client = ApiClient()..setToken(p.token);

    try {
      final data = await ReadingsApi(client).getReadings(
        teamId: p.isTeamLocked ? p.userTeamId : null,
      );
      if (mounted) {
        setState(() => _readings = data.map(ReadingEvent.fromMap).toList());
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erro: $e')));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  String _fmt(DateTime d) {
    return '${d.day.toString().padLeft(2, '0')}/${d.month.toString().padLeft(2, '0')}/${d.year} ${d.hour.toString().padLeft(2, '0')}:${d.minute.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    final p = Provider.of<AppProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Leituras'),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pushReplacementNamed(context, p.homeRoute),
        ),
        actions: [IconButton(icon: const Icon(Icons.refresh), onPressed: _loadReadings)],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _readings.isEmpty
              ? const Center(child: Text('Nenhuma leitura registrada'))
              : ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: _readings.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (context, i) {
                    final r = _readings[i];
                    return Card(
                      child: ListTile(
                        leading: Icon(Icons.receipt_long, color: AppColors.primary),
                        title: Text('${r.teamName} • ${foodCategoryLabel(r.category)}'),
                        subtitle: Text('${r.userName ?? "—"} • ${r.kgAmount.toStringAsFixed(1)} kg • ${_fmt(r.timestamp)}'),
                      ),
                    );
                  },
                ),
    );
  }
}
