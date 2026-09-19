import 'package:flutter/material.dart';

import '../services/skill_analyzer.dart';
import '../widgets/progress_card.dart';
import 'home_screen.dart';
import 'projects_screen.dart';
import 'roadmap_screen.dart';

class ResultScreen extends StatelessWidget {
  final AnalysisResult result;
  const ResultScreen({super.key, required this.result});

  Widget skillSection(BuildContext context, String title, String icon, List<String> skills, Color color) {
    return Card(elevation: 0, margin: const EdgeInsets.only(bottom: 14), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18), side: const BorderSide(color: Color(0xFFDDE5E1))), child: Padding(padding: const EdgeInsets.all(18), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Row(children: [Text(icon, style: const TextStyle(fontSize: 18)), const SizedBox(width: 8), Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16))]), const SizedBox(height: 14), if (skills.isEmpty) Text('Nothing here. Keep going!', style: TextStyle(color: Colors.grey.shade600)) else Wrap(spacing: 8, runSpacing: 8, children: skills.map((skill) => Chip(label: Text(skill), backgroundColor: color.withValues(alpha: .12), side: BorderSide.none, labelStyle: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.w600))).toList())])));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Your results'), actions: [IconButton(tooltip: 'Start over', onPressed: () => Navigator.of(context).pushAndRemoveUntil(MaterialPageRoute(builder: (_) => const HomeScreen()), (_) => false), icon: const Icon(Icons.refresh_rounded))]),
      body: SafeArea(child: ListView(padding: const EdgeInsets.fromLTRB(20, 12, 20, 30), children: [
        Text(result.role.name, style: TextStyle(color: Colors.grey.shade600, fontSize: 14)),
        const SizedBox(height: 4),
        const Text('Your skill snapshot', style: TextStyle(fontSize: 30, fontWeight: FontWeight.bold)),
        const SizedBox(height: 22),
        ProgressCard(percentage: result.matchPercentage),
        const SizedBox(height: 24),
        skillSection(context, 'Skills You Have', '✅', result.skillsYouHave.map((skill) => skill.name).toList(), const Color(0xFF2D8A61)),
        skillSection(context, 'Skills You Need', '❌', result.missingSkills.map((skill) => skill.name).toList(), const Color(0xFFD35E39)),
        skillSection(context, 'High Priority', '🔥', result.highPriority.map((skill) => skill.name).toList(), const Color(0xFFD35E39)),
        skillSection(context, 'Medium Priority', '📌', result.mediumPriority.map((skill) => skill.name).toList(), const Color(0xFF9B7817)),
        const SizedBox(height: 8),
        Row(children: [Expanded(child: FilledButton.icon(onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => RoadmapScreen(result: result))), icon: const Icon(Icons.route_rounded), label: const Text('Roadmap'), style: FilledButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 15)))), const SizedBox(width: 10), Expanded(child: OutlinedButton.icon(onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => ProjectsScreen(result: result))), icon: const Icon(Icons.rocket_launch_outlined), label: const Text('Projects'), style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 15))))]),
      ])),
    );
  }
}
