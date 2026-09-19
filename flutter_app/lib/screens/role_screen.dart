import 'package:flutter/material.dart';

import '../data/skill_database.dart';
import '../models/job_role.dart';
import '../widgets/skill_card.dart';
import 'skills_screen.dart';

class RoleScreen extends StatefulWidget {
  const RoleScreen({super.key});

  @override
  State<RoleScreen> createState() => _RoleScreenState();
}

class _RoleScreenState extends State<RoleScreen> {
  JobRole? selectedRole;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Step 1 of 2')),
      body: SafeArea(child: Column(children: [
        Expanded(child: ListView(padding: const EdgeInsets.fromLTRB(20, 12, 20, 16), children: [
          const Text('What job are you\npreparing for?', style: TextStyle(fontSize: 32, height: 1.08, fontWeight: FontWeight.bold)),
          const SizedBox(height: 10),
          Text('Choose the role that feels closest to your goal.', style: TextStyle(color: Colors.grey.shade600, fontSize: 15)),
          const SizedBox(height: 24),
          ...skillDatabase.map((role) => Padding(padding: const EdgeInsets.only(bottom: 12), child: SkillCard(role: role, selected: selectedRole == role, onTap: () => setState(() => selectedRole = role)))),
        ])),
        Padding(padding: const EdgeInsets.fromLTRB(20, 8, 20, 20), child: SizedBox(width: double.infinity, child: FilledButton(onPressed: selectedRole == null ? null : () => Navigator.push(context, MaterialPageRoute(builder: (_) => SkillsScreen(role: selectedRole!))), style: FilledButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 17), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14))), child: const Text('Continue')))),
      ])),
    );
  }
}
