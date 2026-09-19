import 'package:flutter/material.dart';

import '../services/skill_analyzer.dart';
import '../widgets/roadmap_card.dart';

class RoadmapScreen extends StatelessWidget {
  final AnalysisResult result;
  const RoadmapScreen({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    final learningSkills = [...result.highPriority, ...result.mediumPriority].map((skill) => skill.name).toList();
    final steps = <String>[...learningSkills.take(4), 'Build a ${result.role.name} project'];
    if (steps.length == 1) steps.insert(0, 'Strengthen your existing foundation');
    return Scaffold(appBar: AppBar(title: const Text('Learning roadmap')), body: ListView(padding: const EdgeInsets.fromLTRB(20, 18, 20, 30), children: [const Text('A calm path forward.', style: TextStyle(fontSize: 30, fontWeight: FontWeight.bold)), const SizedBox(height: 8), Text('Focus on one week at a time. Practice beats collecting tutorials.', style: TextStyle(color: Colors.grey.shade600, fontSize: 15)), const SizedBox(height: 28), ...steps.asMap().entries.map((entry) => RoadmapCard(week: entry.key + 1, title: entry.value, isLast: entry.key == steps.length - 1)), const SizedBox(height: 8), Card(elevation: 0, color: const Color(0xFFDDF3E7), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)), child: const Padding(padding: EdgeInsets.all(20), child: Row(children: [Icon(Icons.tips_and_updates_outlined, color: Color(0xFF2D7256)), SizedBox(width: 12), Expanded(child: Text('Keep a small project journal. It will make interviews and presentations much easier.', style: TextStyle(height: 1.4, fontWeight: FontWeight.w600)))]))) ]));
  }
}
