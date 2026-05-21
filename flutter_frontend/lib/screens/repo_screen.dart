import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'branch_screen.dart';

import 'package:url_launcher/url_launcher.dart';
import 'login_screen.dart';

class RepoScreen extends StatefulWidget {
  final String jwt;
  final String username;

  const RepoScreen({super.key, required this.jwt, required this.username});

  @override
  State<RepoScreen> createState() => _RepoScreenState();
}

class _RepoScreenState extends State<RepoScreen> {
  final ApiService api = ApiService();

  List repos = [];
  bool loading = true;

  Future<void> logout(BuildContext context) async {
    await launchUrl(
      Uri.parse("https://github.com/logout"),
      mode: LaunchMode.externalApplication,
    );

    if (context.mounted) {
      Navigator.pushAndRemoveUntil(
        context,
        MaterialPageRoute(builder: (_) => const LoginScreen()),
        (route) => false,
      );
    }
  }

  @override
  void initState() {
    super.initState();
    loadRepos();
  }

  Future<void> loadRepos() async {
    final data = await api.fetchRepos(widget.jwt);

    setState(() {
      repos = data;
      loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Welcome ${widget.username}"),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => logout(context),
          ),
        ],
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: repos.length,
              itemBuilder: (context, index) {
                final repo = repos[index];

                return ListTile(
                  title: Text(repo["name"]),
                  subtitle: Text(repo["private"] ? "Private" : "Public"),
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => BranchScreen(
                          jwt: widget.jwt,
                          repoName: repo["name"],
                        ),
                      ),
                    );
                  },
                );
              },
            ),
    );
  }
}
