import 'package:flutter/material.dart';

import '../services/skill_analyzer.dart';

class ProjectIdea {
  final String name;
  final String skills;
  final String difficulty;
  final String description;
  const ProjectIdea(this.name, this.skills, this.difficulty, this.description);
}

class ProjectsScreen extends StatelessWidget {
  final AnalysisResult result;
  const ProjectsScreen({super.key, required this.result});

  List<ProjectIdea> get ideas {
    final missing = result.missingSkills.map((skill) => skill.name).toSet();
    final recommendations = <ProjectIdea>[];
    if (missing.contains('React') && missing.contains('REST API')) recommendations.add(const ProjectIdea('Student Task Management App', 'React + REST API', 'Intermediate', 'Create tasks, update their status, and connect the interface to a small API.'));
    if (missing.contains('Python') && missing.contains('SQL')) recommendations.add(const ProjectIdea('Student Expense Tracker', 'Python + SQL', 'Beginner', 'Record expenses, filter by category, and show a monthly summary.'));
    if (missing.contains('Java') && missing.contains('SQL')) recommendations.add(const ProjectIdea('Library Management System', 'Java + SQL', 'Intermediate', 'Manage books, borrowers, and return dates with clean CRUD screens.'));
    recommendations.add(ProjectIdea('${result.role.name} Portfolio Project', result.missingSkills.take(3).map((skill) => skill.name).join(' + '), 'Practical', 'Build one focused project that demonstrates the skills you are learning.'));
    return recommendations.take(3).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: const Text('Project ideas')), body: ListView(padding: const EdgeInsets.fromLTRB(20, 18, 20, 30), children: [const Text('Learn by building.', style: TextStyle(fontSize: 30, fontWeight: FontWeight.bold)), const SizedBox(height: 8), Text('Each project gives your new skills somewhere to live.', style: TextStyle(color: Colors.grey.shade600, fontSize: 15)), const SizedBox(height: 26), ...ideas.map((project) => Card(elevation: 0, margin: const EdgeInsets.only(bottom: 14), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18), side: const BorderSide(color: Color(0xFFDDE5E1))), child: Padding(padding: const EdgeInsets.all(20), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [Expanded(child: Text(project.name, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold))), const Icon(Icons.arrow_outward_rounded, color: Color(0xFFF47C50))]), const SizedBox(height: 12), Text(project.description, style: TextStyle(color: Colors.grey.shade700, height: 1.4)), const SizedBox(height: 16), Wrap(spacing: 8, children: [Chip(label: Text(project.skills), backgroundColor: const Color(0xFFDDF3E7), side: BorderSide.none), Chip(label: Text(project.difficulty), backgroundColor: const Color(0xFFFFF0BD), side: BorderSide.none)])])))) ]));
  }
}
