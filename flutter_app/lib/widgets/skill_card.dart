import 'package:flutter/material.dart';

import '../models/job_role.dart';

class SkillCard extends StatelessWidget {
  final JobRole role;
  final bool selected;
  final VoidCallback onTap;

  const SkillCard({super.key, required this.role, required this.selected, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(18),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: selected ? colors.primaryContainer : Colors.white,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: selected ? colors.primary : const Color(0xFFDDE5E1), width: selected ? 2 : 1),
        ),
        child: Row(
          children: [
            CircleAvatar(
              backgroundColor: selected ? colors.primary : const Color(0xFFE8F3EE),
              foregroundColor: selected ? colors.onPrimary : const Color(0xFF2D7256),
              child: Text(role.icon, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            ),
            const SizedBox(width: 14),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(role.name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)), const SizedBox(height: 3), Text(role.description, style: TextStyle(color: Colors.grey.shade600, fontSize: 12))])),
            Icon(selected ? Icons.check_circle : Icons.arrow_forward_ios, size: selected ? 24 : 15, color: selected ? colors.primary : Colors.grey.shade400),
          ],
        ),
      ),
    );
  }
}
