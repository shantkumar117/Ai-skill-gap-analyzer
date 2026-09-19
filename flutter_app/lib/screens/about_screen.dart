import 'package:flutter/material.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  Widget infoCard(String label, String title, String text, IconData icon) {
    return Card(elevation: 0, margin: const EdgeInsets.only(bottom: 14), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18), side: const BorderSide(color: Color(0xFFDDE5E1))), child: Padding(padding: const EdgeInsets.all(20), child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [Icon(icon, color: const Color(0xFF2D7256), size: 27), const SizedBox(width: 15), Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(label, style: const TextStyle(color: Color(0xFFF47C50), fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 1)), const SizedBox(height: 5), Text(title, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold)), const SizedBox(height: 7), Text(text, style: TextStyle(color: Colors.grey.shade600, height: 1.4))]))])));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(appBar: AppBar(title: const Text('About the app')), body: ListView(padding: const EdgeInsets.fromLTRB(20, 18, 20, 30), children: [const Text('Make your next step\nless blurry.', style: TextStyle(fontSize: 30, height: 1.08, fontWeight: FontWeight.bold)), const SizedBox(height: 12), Text('A simple offline MVP for students planning their software careers.', style: TextStyle(color: Colors.grey.shade600, fontSize: 15)), const SizedBox(height: 30), infoCard('THE PROBLEM', 'Where should I focus?', 'Students often collect tutorials without knowing which skills matter most for a target job.', Icons.help_outline_rounded), infoCard('THE SOLUTION', 'A useful comparison.', 'The app compares your skills with predefined job requirements and creates a personalized roadmap.', Icons.compare_arrows_rounded), infoCard('THE TECHNOLOGY', 'Simple by design.', 'Flutter, Dart, local role data, and a transparent rule-based algorithm. No account or internet is needed.', Icons.phone_android_rounded), const SizedBox(height: 12), const Text('Built as a practical college project MVP.', textAlign: TextAlign.center, style: TextStyle(color: Color(0xFF2D7256), fontWeight: FontWeight.w600))]));
  }
}
