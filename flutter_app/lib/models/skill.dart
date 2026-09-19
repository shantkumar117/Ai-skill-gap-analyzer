class Skill {
  final String name;
  final String importance;

  const Skill({required this.name, this.importance = 'Medium'});

  bool get isHighPriority => importance == 'High';
}
