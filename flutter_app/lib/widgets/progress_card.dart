import 'package:flutter/material.dart';

class ProgressCard extends StatelessWidget {
  final int percentage;
  const ProgressCard({super.key, required this.percentage});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0,
      color: const Color(0xFF203B4A),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(22)),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Row(
          children: [
            SizedBox(width: 126, height: 126, child: Stack(alignment: Alignment.center, children: [CircularProgressIndicator(value: percentage / 100, strokeWidth: 11, backgroundColor: Colors.white24, color: const Color(0xFF7BDBAD)), Text('$percentage%', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 28))])),
            const SizedBox(width: 22),
            const Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text('Skill Match', style: TextStyle(color: Colors.white70, fontSize: 14)), SizedBox(height: 8), Text('You are building a strong foundation.', style: TextStyle(color: Colors.white, fontSize: 19, fontWeight: FontWeight.bold)), SizedBox(height: 8), Text('Use the gaps below to choose your next learning step.', style: TextStyle(color: Colors.white70, fontSize: 12))])),
          ],
        ),
      ),
    );
  }
}
