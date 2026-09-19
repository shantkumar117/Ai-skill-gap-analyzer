import 'dart:async';

import 'package:flutter/material.dart';

import '../models/job_role.dart';
import '../services/skill_analyzer.dart';
import 'result_screen.dart';

class AnalysisScreen extends StatefulWidget {
  final JobRole role;
  final List<String> currentSkills;
  const AnalysisScreen({super.key, required this.role, required this.currentSkills});

  @override
  State<AnalysisScreen> createState() => _AnalysisScreenState();
}

class _AnalysisScreenState extends State<AnalysisScreen> {
  @override
  void initState() {
    super.initState();
    Timer(const Duration(milliseconds: 1400), () {
      if (!mounted) return;
      final result = SkillAnalyzer.analyze(widget.role, widget.currentSkills);
      Navigator.of(context).pushReplacement(MaterialPageRoute(builder: (_) => ResultScreen(result: result)));
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
        Container(width: 82, height: 82, decoration: BoxDecoration(color: const Color(0xFFDDF3E7), borderRadius: BorderRadius.circular(24)), child: const Icon(Icons.auto_graph_rounded, size: 42, color: Color(0xFF2D7256))),
        const SizedBox(height: 25),
        const Text('Analyzing your skills...', style: TextStyle(fontSize: 23, fontWeight: FontWeight.bold)),
        const SizedBox(height: 10),
        Text('Comparing your profile with ${widget.role.name}', textAlign: TextAlign.center, style: TextStyle(color: Colors.grey.shade600)),
        const SizedBox(height: 30),
        const SizedBox(width: 25, height: 25, child: CircularProgressIndicator(strokeWidth: 3)),
      ])),
    );
  }
}
