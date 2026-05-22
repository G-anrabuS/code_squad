import 'package:flutter/material.dart';
import '../models/repo_model.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import 'analysis_report_screen.dart';
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
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text("Failed to load repos: $e")));
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
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a GitHub repository URL.')),
      );
      return;
    }

    try {
      setState(() => analyzingUrl = true);
      final report = await _apiService.analyzeRepoUrl(url);

      if (!mounted) return;
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => AnalysisReportScreen(report: report),
        ),
      );
    } catch (e) {
      debugPrint('Analyze URL failed: $e');
      if (!mounted) return;
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('URL analysis failed: $e')));
    } finally {
      if (mounted) {
        setState(() => analyzingUrl = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

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
            Card(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'AI Dashboard',
                      style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Analyze GitHub repositories by selected repo or public URL. Upload ZIP support coming soon.',
                    ),
                    const SizedBox(height: 20),
                    Wrap(
                      spacing: 12,
                      runSpacing: 12,
                      children: [
                        _actionCard(
                          title: 'Upload ZIP',
                          subtitle: 'Drag & drop or browse repo archive',
                          icon: Icons.upload_file,
                          color: theme.colorScheme.primary,
                          buttonLabel: 'Coming soon',
                          enabled: false,
                          onTap: () {},
                        ),
                        _actionCard(
                          title: 'Connect GitHub',
                          subtitle: 'Choose a repository from your account',
                          icon: Icons.link,
                          color: theme.colorScheme.secondary,
                          buttonLabel: 'Refresh',
                          enabled: true,
                          onTap: _loadRepos,
                        ),
                        _actionCard(
                          title: 'Paste Repo URL',
                          subtitle: 'Analyze any public GitHub repo',
                          icon: Icons.code,
                          color: theme.colorScheme.tertiary,
                          buttonLabel: 'Analyze',
                          enabled: true,
                          onTap: _analyzeRepoUrl,
                          child: TextField(
                            controller: _urlController,
                            decoration: const InputDecoration(
                              hintText: 'https://github.com/owner/repo',
                              border: OutlineInputBorder(),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),
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
                              subtitle:
                                  Text(repo.isPrivate ? 'Private' : 'Public'),
                              trailing: const Icon(Icons.arrow_forward_ios),
                              onTap: () {
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (_) => BranchScreen(
                                      repoName: repo.fullName,
                                    ),
                                  ),
                                );
                              },
                            ),
                          );
                        }).toList(),
                      ),
            const SizedBox(height: 40),
            const Text(
              'Quick actions',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Card(
              child: ListTile(
                leading: const Icon(Icons.info_outline),
                title: const Text('Analyze a public GitHub repository by URL'),
                subtitle: const Text('Paste any public repo link and press Analyze.'),
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
                label: Text(analyzingUrl ? 'Analyzing...' : 'Analyze Repository'),
                onPressed: analyzingUrl ? null : _analyzeRepoUrl,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _actionCard({
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
    required String buttonLabel,
    required bool enabled,
    required VoidCallback onTap,
    Widget? child,
  }) {
    return SizedBox(
      width: 320,
      child: Card(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  CircleAvatar(
                    backgroundColor: color.withOpacity(0.16),
                    child: Icon(icon, color: color),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      title,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(subtitle),
              if (child != null) ...[
                const SizedBox(height: 14),
                child,
              ],
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton(
                  onPressed: enabled ? onTap : null,
                  child: Text(buttonLabel),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
