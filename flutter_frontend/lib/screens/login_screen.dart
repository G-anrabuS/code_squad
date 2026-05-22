import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import 'package:flutter_web_auth_2/flutter_web_auth_2.dart';
import '../config/api_config.dart';
import '../services/auth_service.dart';
import '../widgets/app_feedback.dart';
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
              "${ApiConfig.baseUrl}/auth/github/login"
              "?platform=web"
              "&web_origin=${Uri.encodeComponent(Uri.base.origin)}",
          callbackUrlScheme: "https",
        );
      } else {
        result = await FlutterWebAuth2.authenticate(
          url:
              "${ApiConfig.baseUrl}/auth/github/login?platform=mobile",
          callbackUrlScheme: "codesquad",
        );
      }

      final uri = Uri.parse(result);

      final code = uri.queryParameters["code"];

      if (code == null || code.isEmpty) {
        throw Exception("Login code missing");
      }

      final response = await Dio(
        BaseOptions(baseUrl: ApiConfig.baseUrl),
      ).post("/auth/exchange", data: {"code": code});

      final jwt = response.data["jwt"] as String?;
      final username = response.data["username"] as String?;

      if (jwt == null || username == null) {
        throw Exception("Auth response incomplete");
      }

      await _authService.saveAuth(jwt, username);

      if (!mounted) return;

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const RepoScreen()),
      );
    } catch (e) {
      if (!mounted) return;
      showErrorSnackBar(context, "Login failed: $e");
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
