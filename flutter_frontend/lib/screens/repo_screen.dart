import 'package:flutter/material.dart';
import '../models/analysis_report.dart';
import '../models/repo_model.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../widgets/app_feedback.dart';
import 'analysis_loading_screen.dart';
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
  final TextEditingController _urlController = TextEditingController();

  List<RepoModel> repos = [];
  bool loading = true;
  bool analyzingUrl = false;

  @override
  void initState() {
    super.initState();
    _loadRepos();
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  Future<void> _loadRepos() async {
    try {
      setState(() => loading = true);
      repos = await _apiService.getRepos();
    } catch (e) {
      if (!mounted) return;
      showErrorSnackBar(context, "Failed to load repos: $e");
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

  Future<void> _analyzeRepoUrl() async {
    final url = _urlController.text.trim();
    if (url.isEmpty) {
      showErrorSnackBar(context, 'Please enter a GitHub repository URL.');
      return;
    }

    try {
      setState(() => analyzingUrl = true);
      final taskId = await _apiService.startBackgroundAnalysis(repoUrl: url);

      if (!mounted) return;
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => AnalysisLoadingScreen(taskId: taskId),
        ),
      );
    } on AnalysisApiException catch (e) {
      if (!mounted) return;
      showErrorSnackBar(context, e.userMessage);
    } catch (_) {
      if (!mounted) return;
      showErrorSnackBar(context, 'URL analysis failed. Please try again.');
    } finally {
      if (mounted) {
        setState(() => analyzingUrl = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Code Squad'),
        actions: [
          IconButton(onPressed: _logout, icon: const Icon(Icons.logout)),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadRepos,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // 1. QUICK ACTIONS SECTION (MOVED TO TOP)
            const Text(
              'Quick actions',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Card(
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 8.0),
                child: ListTile(
                  leading: const Icon(Icons.info_outline),
                  title: const Text(
                    'Analyze a public GitHub repository by URL',
                  ),
                  subtitle: const Text(
                    'Paste any public repo link and press Analyze.',
                  ),
                ),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _urlController,
              decoration: const InputDecoration(
                hintText: 'https://github.com/owner/repo',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                icon: analyzingUrl
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.flash_on),
                label: Text(
                  analyzingUrl ? 'Analyzing...' : 'Analyze Repository',
                ),
                onPressed: analyzingUrl ? null : _analyzeRepoUrl,
              ),
            ),

            const SizedBox(height: 32),

            // 2. GITHUB REPOSITORY LIST SECTION
            const Text(
              'GitHub Repository List',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            loading
                ? const Center(child: CircularProgressIndicator())
                : repos.isEmpty
                ? const Center(child: Text('No repositories found.'))
                : Column(
                    children: repos.map((repo) {
                      return Card(
                        margin: const EdgeInsets.symmetric(vertical: 8),
                        child: ListTile(
                          title: Text(repo.name),
                          subtitle: Text(repo.isPrivate ? 'Private' : 'Public'),
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
                    }).toList(),
                  ),
          ],
        ),
      ),
    );
  }
}
