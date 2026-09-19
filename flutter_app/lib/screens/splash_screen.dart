import 'dart:async';

import 'package:flutter/material.dart';

import 'home_screen.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    Timer(const Duration(milliseconds: 1600), () {
      if (mounted) {
        Navigator.of(context).pushReplacement(MaterialPageRoute(builder: (_) => const HomeScreen()));
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Scaffold(
      backgroundColor: colors.primary,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
            Container(width: 86, height: 86, decoration: BoxDecoration(color: const Color(0xFF7BDBAD), borderRadius: BorderRadius.circular(26)), child: const Icon(Icons.insights_rounded, size: 48, color: Color(0xFF203B4A))),
            const SizedBox(height: 26),
            const Text('SkillGap AI', style: TextStyle(color: Colors.white, fontSize: 34, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            const Text('Understand your skills. Find your gaps.\nBuild your career.', textAlign: TextAlign.center, style: TextStyle(color: Colors.white70, fontSize: 16, height: 1.5)),
            const SizedBox(height: 48),
            const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF7BDBAD))),
          ]),
        ),
      ),
    );
  }
}
