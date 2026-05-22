import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/analysis_report.dart';
import 'analysis_report_screen.dart';

class AnalysisLoadingScreen extends StatefulWidget {
  final String repoPath;

  const AnalysisLoadingScreen({super.key, required this.repoPath});

  @override
  State<AnalysisLoadingScreen> createState() => _AnalysisLoadingScreenState();
}

class _AnalysisLoadingScreenState extends State<AnalysisLoadingScreen> {
  final ApiService _apiService = ApiService();

  @override
  void initState() {
    super.initState();
    _runAnalysis();
  }

  Future<void> _runAnalysis() async {
    try {
      final AnalysisReport report = await _apiService.analyzeRepo(
        widget.repoPath,
      );

      if (!mounted) return;

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => AnalysisReportScreen(report: report)),
      );
    } catch (e) {
      debugPrint('Analysis request failed: $e');
      if (!mounted) return;

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Analysis failed: $e")));

      Navigator.pop(context);
    }
  }

  @override
  Widget build(BuildContext context) {
    final steps = [
      'Reading codebase',
      'Summary Agent running',
      'Judge Agent pending',
      'Architect Agent pending',
      'Security Agent pending',
      'Performance Agent pending',
      'Generating final report',
    ];

    return Scaffold(
      appBar: AppBar(title: const Text('Analyzing Repository')),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const SizedBox(height: 18),
              const CircularProgressIndicator(strokeWidth: 4),
              const SizedBox(height: 24),
              const Text(
                'Analyzing Codebase...',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 12),
              const Text(
                'AI agents are processing the repository and building the report.',
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              Expanded(
                child: ListView.separated(
                  itemCount: steps.length,
                  separatorBuilder: (_, _) => const Divider(height: 24),
                  itemBuilder: (context, index) {
                    final stage = steps[index];
                    final active = index <= 1;
                    return ListTile(
                      leading: CircleAvatar(
                        backgroundColor: active
                            ? Theme.of(context).colorScheme.primary
                            : Theme.of(
                                context,
                              ).colorScheme.surfaceContainerHighest,
                        child: Icon(
                          active ? Icons.check : Icons.timelapse,
                          color: active ? Colors.white : null,
                          size: 18,
                        ),
                      ),
                      title: Text(stage),
                      subtitle: Text(
                        active ? 'In progress' : 'Waiting',
                        style: const TextStyle(fontSize: 12),
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
