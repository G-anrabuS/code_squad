import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'analysis_loading_screen.dart';

class ScanScreen extends StatefulWidget {
  final String repoName;
  final String branchName;

  const ScanScreen({
    super.key,
    required this.repoName,
    required this.branchName,
  });

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  final ApiService _apiService = ApiService();

  bool loading = false;

  Future<void> _scanRepo() async {
    try {
      setState(() => loading = true);

      final repoPath = await _apiService.scanRepo(
        widget.repoName,
        widget.branchName,
      );

      if (!mounted) return;

      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => AnalysisLoadingScreen(repoPath: repoPath),
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Scan failed: $e")));
    } finally {
      if (mounted) {
        setState(() => loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Scan Repository")),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Card(
              child: ListTile(
                title: Text(widget.repoName),
                subtitle: Text(widget.branchName),
              ),
            ),
            const SizedBox(height: 40),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: loading ? null : _scanRepo,
                child: loading
                    ? const CircularProgressIndicator()
                    : const Text("Scan & Analyze"),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
