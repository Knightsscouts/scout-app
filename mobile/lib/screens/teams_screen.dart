import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

final teamsProvider = FutureProvider((ref) async {
  final response = await Supabase.instance.client
      .from('teams')
      .select()
      .order('team_name');
  return response;
});

class TeamsScreen extends ConsumerWidget {
  const TeamsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final teams = ref.watch(teamsProvider);

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('الفرق الكشفية'),
        ),
        body: teams.when(
          data: (teams) => ListView.builder(
            itemCount: teams.length,
            itemBuilder: (context, index) {
              final team = teams[index];
              return Card(
                margin: const EdgeInsets.all(8),
                child: ListTile(
                  title: Text(team['team_name']),
                  subtitle: Text('القائد: ${team['leader']}'),
                  trailing: Text('النقاط: ${team['points']}'),
                  onTap: () => _showTeamDetails(context, team),
                ),
              );
            },
          ),
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, stack) => Center(
            child: Text('حدث خطأ: $error'),
          ),
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: () => _showAddTeamDialog(context),
          child: const Icon(Icons.add),
        ),
      ),
    );
  }

  void _showTeamDetails(BuildContext context, Map<String, dynamic> team) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(team['team_name']),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('القائد: ${team['leader']}'),
            Text('المساعدين: ${team['assistants']}'),
            Text('النقاط: ${team['points']}'),
            Text('العقوبات: ${team['penalties']}'),
            Text('آخر عهدة: ${team['last_loan']}'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إغلاق'),
          ),
        ],
      ),
    );
  }

  void _showAddTeamDialog(BuildContext context) {
    final formKey = GlobalKey<FormState>();
    String teamName = '', leader = '', assistants = '';

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('إضافة فريق جديد'),
        content: Form(
          key: formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                decoration: const InputDecoration(labelText: 'اسم الفريق'),
                onSaved: (value) => teamName = value ?? '',
                validator: (value) =>
                    value?.isEmpty ?? true ? 'هذا الحقل مطلوب' : null,
              ),
              TextFormField(
                decoration: const InputDecoration(labelText: 'القائد'),
                onSaved: (value) => leader = value ?? '',
                validator: (value) =>
                    value?.isEmpty ?? true ? 'هذا الحقل مطلوب' : null,
              ),
              TextFormField(
                decoration: const InputDecoration(labelText: 'المساعدين'),
                onSaved: (value) => assistants = value ?? '',
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          TextButton(
            onPressed: () async {
              if (formKey.currentState?.validate() ?? false) {
                formKey.currentState?.save();
                try {
                  await Supabase.instance.client.from('teams').insert({
                    'team_name': teamName,
                    'leader': leader,
                    'assistants': assistants,
                    'points': 0,
                    'penalties': '',
                  });
                  Navigator.pop(context);
                } catch (e) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('حدث خطأ: $e')),
                  );
                }
              }
            },
            child: const Text('حفظ'),
          ),
        ],
      ),
    );
  }
}