import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_web_auth_2/flutter_web_auth_2.dart';
import '../services/auth_service.dart';
import 'repo_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  bool _loading = false;
  final AuthService _authService = AuthService();

  Future<void> _login() async {
    try {
      setState(() => _loading = true);

      final String result;

      if (kIsWeb) {
        result = await FlutterWebAuth2.authenticate(
          url:
              "https://code-squad-backend.onrender.com/auth/github/login"
              "?platform=web"
              "&web_origin=${Uri.encodeComponent(Uri.base.origin)}",
          callbackUrlScheme: "https",
        );
      } else {
        result = await FlutterWebAuth2.authenticate(
          url:
              "https://code-squad-backend.onrender.com/auth/github/login?platform=mobile",
          callbackUrlScheme: "codesquad",
        );
      }

      debugPrint("AUTH RESULT: $result");

      final uri = Uri.parse(result);

      final jwt = uri.queryParameters["jwt"];
      final username = uri.queryParameters["username"];

      if (jwt == null || username == null) {
        throw Exception("JWT or username missing");
      }

      await _authService.saveAuth(jwt, username);

      if (!mounted) return;

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const RepoScreen()),
      );
    } catch (e) {
      debugPrint("LOGIN ERROR: $e");

      if (!mounted) return;

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Login failed: $e")));
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  Widget _loginButton() {
    return SizedBox(
      width: 260,
      height: 52,
      child: ElevatedButton.icon(
        onPressed: _loading ? null : _login,
        style: ElevatedButton.styleFrom(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
        ),
        icon: _loading
            ? const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
            : const Icon(Icons.login),
        label: Text(
          _loading ? "Logging in..." : "Login with GitHub",
          style: const TextStyle(fontSize: 16),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.code, size: 90),
              const SizedBox(height: 20),
              const Text(
                "Code Squad",
                style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 10),
              const Text(
                "AI-powered GitHub repository analysis",
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 40),
              _loginButton(),
            ],
          ),
        ),
      ),
    );
  }
}
