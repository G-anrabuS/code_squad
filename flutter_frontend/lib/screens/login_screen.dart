import 'package:flutter/material.dart';
import 'package:flutter_web_auth_2/flutter_web_auth_2.dart';
import 'repo_screen.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  Future<void> login(BuildContext context) async {
    try {
      final result = await FlutterWebAuth2.authenticate(
        url: "https://code-squad-backend.onrender.com/auth/github/login",
        callbackUrlScheme: "codesquad",
      );

      debugPrint("AUTH RESULT: $result");

      final uri = Uri.parse(result);

      final jwt = uri.queryParameters["jwt"];
      final username = uri.queryParameters["username"];

      debugPrint("JWT: $jwt");
      debugPrint("USERNAME: $username");

      if (jwt != null && context.mounted) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => RepoScreen(jwt: jwt, username: username ?? "User"),
          ),
        );
      } else {
        debugPrint("JWT NULL");
      }
    } catch (e) {
      debugPrint("LOGIN ERROR: $e");

      if (context.mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text("Login failed: $e")));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: ElevatedButton(
          onPressed: () => login(context),
          child: const Text("Login with GitHub"),
        ),
      ),
    );
  }
}
