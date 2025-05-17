import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

final logsProvider = FutureProvider((ref) async {
  final response = await Supabase.instance.client
      .from('action_logs')
      .select()
      .order('timestamp', ascending: false);
  return response;
});

class LogsScreen extends ConsumerWidget {
  const LogsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final logs = ref.watch(logsProvider);

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('سجل الإجراءات'),
        ),
        body: logs.when(
          data: (logs) => ListView.builder(
            itemCount: logs.length,
            itemBuilder: (context, index) {
              final log = logs[index];
              return Card(
                margin: const EdgeInsets.all(8),
                child: ListTile(
                  title: Text(log['action']),
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('الفريق: ${log['team_name']}'),
                      Text('التفاصيل: ${log['details']}'),
                      Text('التاريخ: ${log['timestamp']}'),
                    ],
                  ),
                ),
              );
            },
          ),
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, stack) => Center(
            child: Text('حدث خطأ: $error'),
          ),
        ),
      ),
    );
  }
}