import 'package:flutter/material.dart';
import 'package:flutter_web_auth_2/flutter_web_auth_2.dart';
import 'repo_screen.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  Future<void> login(BuildContext context) async {
    final result = await FlutterWebAuth2.authenticate(
      url: "http://10.149.147.205:8000/auth/github/login",
      callbackUrlScheme: "codesquad",
    );

    final uri = Uri.parse(result);

    final jwt = uri.queryParameters["jwt"];
    final username = uri.queryParameters["username"];

    if (jwt != null) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => RepoScreen(jwt: jwt, username: username ?? "User"),
        ),
      );
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
