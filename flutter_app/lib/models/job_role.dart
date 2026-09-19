import 'skill.dart';

class JobRole {
  final String name;
  final String description;
  final String icon;
  final List<Skill> requiredSkills;

  const JobRole({
    required this.name,
    required this.description,
    required this.icon,
    required this.requiredSkills,
  });
}
