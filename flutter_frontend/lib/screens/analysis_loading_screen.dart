import 'dart:async';

import 'package:flutter/material.dart';

import '../models/analysis_report.dart';
import '../services/api_service.dart';
import '../widgets/app_feedback.dart';
import 'analysis_report_screen.dart';

class AnalysisLoadingScreen extends StatefulWidget {
  final String taskId;

  const AnalysisLoadingScreen({super.key, required this.taskId});

  @override
  State<AnalysisLoadingScreen> createState() => _AnalysisLoadingScreenState();
}

class _AnalysisLoadingScreenState extends State<AnalysisLoadingScreen> {
  final ApiService _apiService = ApiService();
  Timer? _pollingTimer;
  bool _isPolling = false;

  AnalysisProgress _progress = AnalysisProgress(
    status: 'pending',
    steps: const {
      'scan': 'pending',
      'summary': 'pending',
      'judge': 'pending',
      'architect': 'pending',
      'performance': 'pending',
      'security': 'pending',
    },
  );
  bool _navigated = false;

  @override
  void initState() {
    super.initState();
    _pollProgress();
    _pollingTimer = Timer.periodic(
      const Duration(seconds: 2),
      (_) => _pollProgress(),
    );
  }

  @override
  void dispose() {
    _pollingTimer?.cancel();
    super.dispose();
  }

  Future<void> _pollProgress() async {
    if (_isPolling || _navigated || !mounted) return;

    _isPolling = true;

    try {
      final progress = await _apiService.getAnalysisProgress(widget.taskId);

      if (!mounted || _navigated) return;

      setState(() {
        _progress = progress;
      });

      if (progress.status == 'completed') {
        await _loadFinalResult();
        return;
      }

      if (progress.status == 'failed') {
        _stopPolling();
        showErrorSnackBar(
          context,
          progress.message ?? 'Analysis failed. Please try again.',
        );

        if (mounted && Navigator.canPop(context) && !_navigated) {
          _navigated = true;
          Navigator.pop(context);
        }
      }
    } on AnalysisApiException catch (e) {
      if (!mounted) return;

      _stopPolling();
      showErrorSnackBar(context, e.userMessage);

      if (Navigator.canPop(context) && !_navigated) {
        _navigated = true;
        Navigator.pop(context);
      }
    } catch (_) {
      if (!mounted) return;

      _stopPolling();
      showErrorSnackBar(context, 'Analysis failed. Please try again.');

      if (Navigator.canPop(context) && !_navigated) {
        _navigated = true;
        Navigator.pop(context);
      }
    } finally {
      _isPolling = false;
    }
  }

  Future<void> _loadFinalResult() async {
    final result = await _apiService.getAnalysisResult(widget.taskId);

    if (!mounted || _navigated) return;

    if (result.status == 'completed' && result.data != null) {
      _stopPolling();
      _navigated = true;

      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) => AnalysisReportScreen(report: result.data!),
        ),
      );
      return;
    }

    _stopPolling();
    showErrorSnackBar(
      context,
      result.message ?? 'Analysis failed. Please try again.',
    );

    if (mounted && Navigator.canPop(context) && !_navigated) {
      _navigated = true;
      Navigator.pop(context);
    }
  }

  void _stopPolling() {
    _pollingTimer?.cancel();
    _pollingTimer = null;
  }

  String _stepLabel(String step) {
    switch (step) {
      case 'scan':
        return 'Reading codebase';
      case 'summary':
        return 'Summary Agent';
      case 'judge':
        return 'Judge Agent';
      case 'architect':
        return 'Architecture Agent';
      case 'performance':
        return 'Performance Agent';
      case 'security':
        return 'Security Agent';
      default:
        return step;
    }
  }

  Widget _stepIcon(BuildContext context, String status) {
    switch (status) {
      case 'completed':
        return const Icon(Icons.check_circle, color: Colors.green);
      case 'running':
        return const SizedBox(
          width: 22,
          height: 22,
          child: CircularProgressIndicator(strokeWidth: 2),
        );
      case 'failed':
        return const Icon(Icons.error, color: Colors.redAccent);
      default:
        return Icon(
          Icons.radio_button_unchecked,
          color: Theme.of(context).colorScheme.outline,
        );
    }
  }

  String _stepSubtitle(String status) {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'running':
        return 'Running';
      case 'failed':
        return 'Failed';
      default:
        return 'Pending';
    }
  }

  @override
  Widget build(BuildContext context) {
    final stepOrder = [
      'scan',
      'summary',
      'judge',
      'architect',
      'performance',
      'security',
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
              if ((_progress.message ?? '').isNotEmpty) ...[
                const SizedBox(height: 12),
                Text(
                  _progress.message!,
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
              const SizedBox(height: 32),
              Expanded(
                child: ListView.separated(
                  itemCount: stepOrder.length,
                  separatorBuilder: (_, _) => const Divider(height: 24),
                  itemBuilder: (context, index) {
                    final step = stepOrder[index];
                    final status = _progress.steps[step] ?? 'pending';
                    return ListTile(
                      leading: _stepIcon(context, status),
                      title: Text(_stepLabel(step)),
                      subtitle: Text(
                        _stepSubtitle(status),
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
