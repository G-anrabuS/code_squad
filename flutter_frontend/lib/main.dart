import 'package:flutter/material.dart';
import 'screens/login_screen.dart';

void main() {
  runApp(const CodeSquadApp());
}

class CodeSquadApp extends StatelessWidget {
  const CodeSquadApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(debugShowCheckedModeBanner: false, home: LoginScreen());
  }
}
