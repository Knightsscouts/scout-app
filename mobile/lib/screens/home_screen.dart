import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'teams_screen.dart';
import 'inventory_screen.dart';
import 'logs_screen.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('مجموعة البشارة المفرحة الكشفية'),
          centerTitle: true,
        ),
        body: GridView.count(
          padding: const EdgeInsets.all(16),
          crossAxisCount: 2,
          children: [
            _buildMenuItem(
              context,
              'الفرق الكشفية',
              Icons.group,
              () => Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const TeamsScreen()),
              ),
            ),
            _buildMenuItem(
              context,
              'العهدة',
              Icons.inventory,
              () => Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const InventoryScreen()),
              ),
            ),
            _buildMenuItem(
              context,
              'السجل',
              Icons.history,
              () => Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const LogsScreen()),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMenuItem(
    BuildContext context,
    String title,
    IconData icon,
    VoidCallback onTap,
  ) {
    return Card(
      elevation: 4,
      child: InkWell(
        onTap: onTap,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 48),
            const SizedBox(height: 8),
            Text(
              title,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
    );
  }
}