import 'package:flutter/material.dart';

class RoadmapCard extends StatelessWidget {
  final int week;
  final String title;
  final bool isLast;

  const RoadmapCard({super.key, required this.week, required this.title, this.isLast = false});

  @override
  Widget build(BuildContext context) {
    return IntrinsicHeight(
      child: Row(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
        SizedBox(width: 42, child: Column(children: [CircleAvatar(radius: 17, backgroundColor: const Color(0xFFE0F2E8), child: Text('$week', style: const TextStyle(color: Color(0xFF2D7256), fontWeight: FontWeight.bold, fontSize: 12))), if (!isLast) Expanded(child: Container(width: 2, color: const Color(0xFFD5E8DD)))])),
        Expanded(child: Container(margin: const EdgeInsets.only(bottom: 14), padding: const EdgeInsets.all(16), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), border: Border.all(color: const Color(0xFFDDE5E1))), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text('WEEK $week', style: const TextStyle(color: Color(0xFFF47C50), fontWeight: FontWeight.bold, fontSize: 11, letterSpacing: 1)), const SizedBox(height: 5), Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16))]))),
      ]),
    );
  }
}
