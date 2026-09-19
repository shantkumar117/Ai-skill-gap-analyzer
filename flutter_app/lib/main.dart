import 'package:flutter/material.dart';

import 'screens/splash_screen.dart';

void main() {
  runApp(const SkillGapApp());
}

class SkillGapApp extends StatelessWidget {
  const SkillGapApp({super.key});

  @override
  Widget build(BuildContext context) {
    const navy = Color(0xFF203B4A);
    return MaterialApp(
      title: 'AI Skill Gap Analyzer',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF55B88B)),
        scaffoldBackgroundColor: const Color(0xFFF7F8F4),
        fontFamily: 'sans',
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFFF7F8F4),
          foregroundColor: navy,
          elevation: 0,
          centerTitle: false,
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.all(Radius.circular(14)),
            borderSide: BorderSide(color: Color(0xFFDDE5E1)),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.all(Radius.circular(14)),
            borderSide: BorderSide(color: Color(0xFFDDE5E1)),
          ),
        ),
      ),
      home: const SplashScreen(),
    );
  }
}
