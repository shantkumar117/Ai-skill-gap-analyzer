import 'package:flutter/material.dart';

import '../data/skill_database.dart';
import '../models/job_role.dart';
import 'analysis_screen.dart';

class SkillsScreen extends StatefulWidget {
  final JobRole role;
  const SkillsScreen({super.key, required this.role});

  @override
  State<SkillsScreen> createState() => _SkillsScreenState();
}

class _SkillsScreenState extends State<SkillsScreen> {
  final selectedSkills = <String>{};
  final customSkillController = TextEditingController();

  @override
  void dispose() {
    customSkillController.dispose();
    super.dispose();
  }

  void toggleSkill(String skill) {
    setState(() {
      if (!selectedSkills.remove(skill)) selectedSkills.add(skill);
    });
  }

  void addCustomSkill() {
    final value = customSkillController.text.trim();
    if (value.isNotEmpty) {
      setState(() => selectedSkills.add(value));
      customSkillController.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(title: const Text('Step 2 of 2')),
      body: SafeArea(child: Column(children: [
        Expanded(child: ListView(padding: const EdgeInsets.fromLTRB(20, 12, 20, 16), children: [
          const Text('What skills do you\ncurrently have?', style: TextStyle(fontSize: 32, height: 1.08, fontWeight: FontWeight.bold)),
          const SizedBox(height: 10),
          Text('Select what you know. It is okay to start small.', style: TextStyle(color: Colors.grey.shade600, fontSize: 15)),
          const SizedBox(height: 25),
          Wrap(spacing: 9, runSpacing: 9, children: commonSkillNames.map((skill) => FilterChip(label: Text(skill), selected: selectedSkills.contains(skill), onSelected: (_) => toggleSkill(skill), selectedColor: colors.primaryContainer, checkmarkColor: colors.primary, side: const BorderSide(color: Color(0xFFDDE5E1)))).toList()),
          const SizedBox(height: 28),
          const Text('Add another skill', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 9),
          Row(children: [Expanded(child: TextField(controller: customSkillController, textInputAction: TextInputAction.done, onSubmitted: (_) => addCustomSkill(), decoration: const InputDecoration(hintText: 'e.g. Docker'))), const SizedBox(width: 9), IconButton.filled(onPressed: addCustomSkill, icon: const Icon(Icons.add), tooltip: 'Add skill')]),
          if (selectedSkills.isNotEmpty) ...[const SizedBox(height: 25), Text('${selectedSkills.length} skills selected', style: TextStyle(color: Color(0xFF2D7256), fontWeight: FontWeight.bold))],
        ])),
        Padding(
          padding: const EdgeInsets.fromLTRB(20, 8, 20, 20),
          child: SizedBox(
            width: double.infinity,
            child: FilledButton.icon(
              onPressed: selectedSkills.isEmpty
                  ? null
                  : () => Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => AnalysisScreen(
                            role: widget.role,
                            currentSkills: selectedSkills.toList(),
                          ),
                        ),
                      ),
              icon: const Icon(Icons.insights_rounded),
              label: const Text('Analyze My Skills'),
              style: FilledButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 17),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
              ),
            ),
          ),
        ),
      ])),
    );
  }
}
