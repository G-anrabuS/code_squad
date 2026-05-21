import 'package:flutter/material.dart';
import '../models/repo_model.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import 'branch_screen.dart';
import 'login_screen.dart';

class RepoScreen extends StatefulWidget {
  const RepoScreen({super.key});

  @override
  State<RepoScreen> createState() => _RepoScreenState();
}

class _RepoScreenState extends State<RepoScreen> {
  final ApiService _apiService = ApiService();
  final AuthService _authService = AuthService();

  List<RepoModel> repos = [];
  bool loading = true;

  @override
  void initState() {
    super.initState();
    _loadRepos();
  }

  Future<void> _loadRepos() async {
    try {
      setState(() => loading = true);

      repos = await _apiService.getRepos();
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Failed to load repos: $e")));
    } finally {
      if (mounted) {
        setState(() => loading = false);
      }
    }
  }

  Future<void> _logout() async {
    await _authService.logout();

    if (!mounted) return;

    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => const LoginScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Your GitHub Repositories"),
        actions: [
          IconButton(onPressed: _logout, icon: const Icon(Icons.logout)),
        ],
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadRepos,
              child: ListView.builder(
                itemCount: repos.length,
                itemBuilder: (context, index) {
                  final repo = repos[index];

                  return Card(
                    margin: const EdgeInsets.all(8),
                    child: ListTile(
                      title: Text(repo.name),
                      subtitle: Text(repo.isPrivate ? "Private" : "Public"),
                      trailing: const Icon(Icons.arrow_forward_ios),
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) =>
                                BranchScreen(repoName: repo.fullName),
                          ),
                        );
                      },
                    ),
                  );
                },
              ),
            ),
    );
  }
}
