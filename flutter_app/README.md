# AI Skill Gap Analyzer - Flutter MVP

An offline Flutter application for students who want a practical learning plan for a software career. The MVP uses a local skill database and a transparent rule-based analyzer. It needs no Firebase, login, internet connection, or AI API.

## 1. Install Flutter

1. Install the stable Flutter SDK from https://docs.flutter.dev/get-started/install.
2. Add Flutter's `bin` folder to your PATH.
3. Install Android Studio and an Android SDK/emulator, or enable USB debugging on a physical Android phone.
4. In a terminal, run:

```powershell
flutter doctor
```

Resolve the Android toolchain items marked with an error before running on Android.

## 2. Create native project files

This repository contains the complete Dart source. Because Flutter is not installed in the generation environment, create the standard Android wrapper once after installing Flutter:

```powershell
cd flutter_app
flutter create --platforms=android .
```

This preserves the existing `lib/` and `pubspec.yaml` files and creates the Android runner files.

## 3. Run in VS Code

Open the `flutter_app` folder in VS Code. Install the Flutter and Dart extensions, choose an emulator or connected phone, then run:

```powershell
flutter pub get
flutter analyze
flutter run
```

The app starts with the Splash screen and then opens the Home screen.

## 4. Run on an Android phone

1. Enable Developer Options and USB debugging on the phone.
2. Connect the phone by USB and accept the debugging prompt.
3. Check the connection with `flutter devices`.
4. Run `flutter run` from this folder.

## Architecture

```text
lib/
├── main.dart
├── models/       # Skill and JobRole data classes
├── data/         # Expandable local role and skill database
├── services/     # Offline match calculation and result model
├── screens/      # Splash, home, role, skills, analysis, result, roadmap, projects, about
└── widgets/      # Reusable role cards, progress card, roadmap card
```

## How the calculation works

For the selected role, the analyzer counts how many required skills appear in the user's selected or typed skills. It compares names case-insensitively:

`match percentage = (skills you have / total required skills) * 100`

The result is rounded to the nearest whole number. Missing skills are split into High and Medium priority using the importance stored in the local database.

## Adding AI later

The MVP intentionally uses local deterministic recommendations. A future version could:

- Add an optional OpenAI-compatible API behind an environment variable or secure backend.
- Send only the selected role, current skills, and missing skills to generate richer explanations.
- Keep the local analyzer as a fallback when the API is unavailable.

Never put a private API key directly in a Flutter client app. Use a small backend proxy for production.

## Future final-year improvements

- Firebase Authentication for accounts.
- Firestore for saved analyses and progress history.
- Resume upload and server-side skill extraction.
- Weekly progress tracking, reminders, and curated course links.
- Admin panel for editing the role-skill database.
- Research-based recommendation evaluation and a comparison with the rule-based baseline.
