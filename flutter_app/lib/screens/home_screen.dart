import 'package:flutter/material.dart';

import 'about_screen.dart';
import 'role_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(24, 42, 24, 28),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
              Row(children: [Container(width: 38, height: 38, decoration: BoxDecoration(color: const Color(0xFF203B4A), borderRadius: BorderRadius.circular(11)), child: const Icon(Icons.insights_rounded, color: Colors.white, size: 21)), const SizedBox(width: 10), const Text('SkillGap AI', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 17))]),
              IconButton(tooltip: 'About app', onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const AboutScreen())), icon: const Icon(Icons.info_outline)),
            ]),
            const SizedBox(height: 62),
            const Text('Your next career\nmove starts here.', style: TextStyle(fontSize: 39, height: 1.04, fontWeight: FontWeight.bold, color: Color(0xFF203B4A))),
            const SizedBox(height: 22),
            Text('Discover the skills you need for your dream software career.', style: TextStyle(fontSize: 17, height: 1.45, color: Colors.grey.shade600)),
            const SizedBox(height: 38),
            Container(padding: const EdgeInsets.all(22), decoration: BoxDecoration(color: const Color(0xFFDDF3E7), borderRadius: BorderRadius.circular(24)), child: Row(children: [const Icon(Icons.lightbulb_outline_rounded, color: Color(0xFF2D7256), size: 31), const SizedBox(width: 16), Expanded(child: Text('Get a simple learning plan based on the role you want.', style: TextStyle(color: Colors.grey.shade800, fontWeight: FontWeight.w600, height: 1.35)))])),
            const SizedBox(height: 30),
            SizedBox(width: double.infinity, child: FilledButton.icon(onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const RoleScreen())), icon: const Icon(Icons.arrow_forward_rounded), label: const Text('Start Analysis'), style: FilledButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 17), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14))))),
            const SizedBox(height: 12),
            SizedBox(width: double.infinity, child: OutlinedButton(onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const AboutScreen())), style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 17), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14))), child: const Text('About App'))),
            const SizedBox(height: 48),
            Row(children: [Icon(Icons.lock_outline, size: 16, color: Colors.grey.shade500), const SizedBox(width: 7), Text('Works offline using a local skill database', style: TextStyle(color: Colors.grey.shade500, fontSize: 12))]),
          ]),
        ),
      ),
    );
  }
}
