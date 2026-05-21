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
      if (!mounted) return;

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Analysis failed: $e")));

      Navigator.pop(context);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: const [
              CircularProgressIndicator(),
              SizedBox(height: 24),
              Text(
                "Analyzing Codebase...",
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 12),
              Text(
                "Running heuristic AI agents\nSecurity • Performance • Architecture",
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
