import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../models/analysis_report.dart';

class AnalysisReportScreen extends StatelessWidget {
  final AnalysisReport report;

  const AnalysisReportScreen({super.key, required this.report});

  Widget sectionCard(String title, List<Widget> children) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title,
                style:
                    const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget scorePanel(String label, double value, Color color) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: const TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 10),
            LinearProgressIndicator(value: value, color: color),
            const SizedBox(height: 10),
            Text('${(value * 100).toInt()}%',
                style: const TextStyle(fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }

  Widget issueList(String title, List<dynamic> items) {
    return sectionCard(
      title,
      items.isEmpty
          ? [const Text('No items found.')]
          : items
              .take(8)
              .map((issue) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 6),
                    child: Text('• ${issue.toString()}'),
                  ))
              .toList(),
    );
  }

  Future<void> _copySummary(BuildContext context) async {
    final summary = report.projectSummary.entries
        .map((entry) => '${entry.key}: ${entry.value}')
        .join('\n');

    await Clipboard.setData(ClipboardData(text: summary));
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Summary copied to clipboard')),
      );
    }
  }

  void _exportJson(BuildContext context) {
    final encoded = const JsonEncoder.withIndent('  ').convert(report.raw);
    Clipboard.setData(ClipboardData(text: encoded));
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Report JSON copied to clipboard')),
      );
    }
  }

  void _downloadPdf(BuildContext context) {
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('PDF export coming soon')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final repoInfo = report.repositoryInfo;
    final architecture = report.architectureAnalysis;
    final quality = report.codeQuality;
    final performance = report.performance;
    final security = report.security;
    final recommendations = report.recommendations;

    return DefaultTabController(
      length: 6,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Report Dashboard'),
          actions: [
            IconButton(
              tooltip: 'Copy Summary',
              icon: const Icon(Icons.copy_all),
              onPressed: () => _copySummary(context),
            ),
            IconButton(
              tooltip: 'Export JSON',
              icon: const Icon(Icons.file_download),
              onPressed: () => _exportJson(context),
            ),
            IconButton(
              tooltip: 'Download PDF',
              icon: const Icon(Icons.picture_as_pdf),
              onPressed: () => _downloadPdf(context),
            ),
          ],
          bottom: const TabBar(
            isScrollable: true,
            tabs: [
              Tab(text: 'Overview'),
              Tab(text: 'Code'),
              Tab(text: 'Architecture'),
              Tab(text: 'Security'),
              Tab(text: 'Performance'),
              Tab(text: 'Files'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  sectionCard(
                    'Overview',
                    [
                      scorePanel(
                        'Overall',
                        (report.report['overall_score'] ?? 0).toDouble(),
                        Theme.of(context).colorScheme.primary,
                      ),
                      const SizedBox(height: 14),
                      Text(
                        report.report['summary']?.toString() ??
                            'Summary unavailable.',
                        style: const TextStyle(fontSize: 16),
                      ),
                    ],
                  ),
                  sectionCard(
                    'Repository Info',
                    [
                      Text('Project Type: ${repoInfo['project_type'] ?? 'Unknown'}'),
                      const SizedBox(height: 6),
                      Text(
                        'Tech Stack: ${(repoInfo['tech_stack'] as List?)?.join(', ') ?? 'Unknown'}',
                      ),
                      const SizedBox(height: 6),
                      Text('Total files: ${repoInfo['total_files'] ?? 0}'),
                    ],
                  ),
                ],
              ),
            ),
            SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  scorePanel('Maintainability',
                      (quality['maintainability'] ?? 0).toDouble(), Colors.blue),
                  scorePanel('Readability',
                      (quality['readability'] ?? 0).toDouble(), Colors.green),
                  scorePanel('Modularity',
                      (quality['modularity'] ?? 0).toDouble(), Colors.teal),
                  const SizedBox(height: 12),
                  issueList('Code Quality Notes',
                      quality['issues'] ?? ['No code quality details available.']),
                ],
              ),
            ),
            SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  sectionCard(
                    'Architecture Health',
                    [
                      Text('Current Style: ${architecture['current_pattern'] ?? 'Unknown'}'),
                      const SizedBox(height: 8),
                      Text('Complexity: ${architecture['complexity'] ?? 'Unknown'}'),
                      const SizedBox(height: 8),
                      Text('Maturity: ${architecture['maturity'] ?? 'Unknown'}'),
                    ],
                  ),
                  issueList('Architecture Issues',
                      architecture['issues'] ?? ['No architecture issues available.']),
                ],
              ),
            ),
            SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  sectionCard(
                    'Security Status',
                    [
                      Text('Severity: ${security['severity_level'] ?? 'Unknown'}'),
                      const SizedBox(height: 8),
                      Text('Finding count: ${(security['issues'] as List?)?.length ?? 0}'),
                    ],
                  ),
                  issueList('Critical Security Risks',
                      security['critical_issues'] ?? ['No critical issues found.']),
                ],
              ),
            ),
            SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  issueList('Performance Suggestions',
                      performance['recommendations'] ?? ['No performance recommendations.']),
                  issueList('Optimization Opportunities',
                      performance['opportunities'] ?? ['No optimization opportunities.']),
                ],
              ),
            ),
            SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  issueList('Top File Risks',
                      report.report['files'] ?? ['File review not available.']),
                  sectionCard(
                    'Raw File Data',
                    [
                      SelectableText(
                        const JsonEncoder.withIndent('  ').convert(
                          report.report['files'] ?? {'info': 'No file data'},
                        ),
                        style: const TextStyle(fontFamily: 'monospace'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
