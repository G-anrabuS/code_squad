import 'package:flutter/material.dart';
import 'screens/login_screen.dart';
import 'screens/repo_screen.dart';
import 'services/auth_service.dart';

void main() {
  runApp(const CodeSquadApp());
}

class CodeSquadApp extends StatelessWidget {
  const CodeSquadApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: "Code Squad",
      theme: ThemeData(useMaterial3: true, brightness: Brightness.dark),
      home: const AppEntry(),
    );
  }
}

class AppEntry extends StatefulWidget {
  const AppEntry({super.key});

  @override
  State<AppEntry> createState() => _AppEntryState();
}

class _AppEntryState extends State<AppEntry> {
  final AuthService _authService = AuthService();

  bool _loading = true;
  bool _loggedIn = false;

  @override
  void initState() {
    super.initState();
    _checkLogin();
  }

  Future<void> _checkLogin() async {
    final loggedIn = await _authService.isLoggedIn();

    setState(() {
      _loggedIn = loggedIn;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    return _loggedIn ? const RepoScreen() : const LoginScreen();
  }
}
