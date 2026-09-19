import '../models/job_role.dart';
import '../models/skill.dart';

class AnalysisResult {
  final JobRole role;
  final List<String> currentSkills;
  final List<Skill> skillsYouHave;
  final List<Skill> missingSkills;
  final List<Skill> highPriority;
  final List<Skill> mediumPriority;
  final int matchPercentage;

  const AnalysisResult({
    required this.role,
    required this.currentSkills,
    required this.skillsYouHave,
    required this.missingSkills,
    required this.highPriority,
    required this.mediumPriority,
    required this.matchPercentage,
  });
}

class SkillAnalyzer {
  static AnalysisResult analyze(JobRole role, List<String> currentSkills) {
    final normalizedCurrent = currentSkills.map(_normalize).toSet();
    final skillsYouHave = role.requiredSkills
        .where((skill) => normalizedCurrent.contains(_normalize(skill.name)))
        .toList();
    final missingSkills = role.requiredSkills
        .where((skill) => !normalizedCurrent.contains(_normalize(skill.name)))
        .toList();
    final match = ((skillsYouHave.length / role.requiredSkills.length) * 100).round();

    return AnalysisResult(
      role: role,
      currentSkills: currentSkills,
      skillsYouHave: skillsYouHave,
      missingSkills: missingSkills,
      highPriority: missingSkills.where((skill) => skill.isHighPriority).toList(),
      mediumPriority: missingSkills.where((skill) => !skill.isHighPriority).toList(),
      matchPercentage: match,
    );
  }

  static String _normalize(String value) => value.trim().toLowerCase();
}
