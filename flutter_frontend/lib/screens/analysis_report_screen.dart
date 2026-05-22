import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../models/analysis_report.dart';

class AnalysisReportScreen extends StatelessWidget {
  final AnalysisReport report;

  const AnalysisReportScreen({super.key, required this.report});

  bool _agentFailed(Map<String, dynamic> section) => section['status'] == 'error';

  String _agentUnavailableTitle(String title) {
    switch (title) {
      case 'Architecture Review':
        return 'Architecture analysis unavailable';
      case 'Performance Review':
        return 'Performance analysis unavailable';
      case 'Security Review':
        return 'Security analysis unavailable';
      case 'Judge Review':
        return 'Judge analysis unavailable';
      case 'Summary Agent':
        return 'Summary analysis unavailable';
      default:
        return '$title unavailable';
    }
  }

  Future<void> _copyJson(BuildContext context) async {
    final encoded = const JsonEncoder.withIndent('  ').convert(report.raw);
    await Clipboard.setData(ClipboardData(text: encoded));
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Report JSON copied to clipboard')),
      );
    }
  }

  Widget _sectionCard(BuildContext context, String title, List<Widget> children) {
    final scheme = Theme.of(context).colorScheme;
    return Card(
      color: scheme.surfaceContainerLow,
      margin: const EdgeInsets.symmetric(vertical: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: Theme.of(
                context,
              ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 14),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _overviewRow(BuildContext context, String label, String value) {
    final style = Theme.of(context).textTheme.bodyMedium;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: style?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value.isEmpty ? 'Unavailable' : value,
              style: style?.copyWith(fontWeight: FontWeight.w600),
            ),
          ),
        ],
      ),
    );
  }

  Widget _scoreBadge(BuildContext context) {
    final score = report.overallScore;
    final scheme = Theme.of(context).colorScheme;
    final normalized = (score / 100).clamp(0.0, 1.0);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: scheme.primaryContainer,
        borderRadius: BorderRadius.circular(18),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Overall Score',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              color: scheme.onPrimaryContainer,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 10),
          LinearProgressIndicator(
            value: normalized,
            minHeight: 10,
            borderRadius: BorderRadius.circular(999),
          ),
          const SizedBox(height: 10),
          Text(
            score.toStringAsFixed(1),
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
              color: scheme.onPrimaryContainer,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _severityBadge(BuildContext context, String? severity) {
    final value = (severity ?? '').trim();
    if (value.isEmpty) return const SizedBox.shrink();

    final scheme = Theme.of(context).colorScheme;
    Color background = scheme.secondaryContainer;
    Color foreground = scheme.onSecondaryContainer;
    final upper = value.toUpperCase();

    if (upper.contains('CRITICAL') || upper.contains('HIGH')) {
      background = scheme.errorContainer;
      foreground = scheme.onErrorContainer;
    } else if (upper.contains('MEDIUM')) {
      background = Colors.orange.withValues(alpha: 0.18);
      foreground = Colors.orange.shade200;
    } else if (upper.contains('LOW')) {
      background = Colors.green.withValues(alpha: 0.16);
      foreground = Colors.green.shade200;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: background,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        upper,
        style: TextStyle(fontWeight: FontWeight.w700, color: foreground),
      ),
    );
  }

  Widget _recommendationList(List<dynamic> items) {
    if (items.isEmpty) {
      return const Text('No recommendations available.');
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: items
          .map(
            (item) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Padding(
                    padding: EdgeInsets.only(top: 3, right: 8),
                    child: Icon(Icons.circle, size: 8),
                  ),
                  Expanded(child: Text(item.toString())),
                ],
              ),
            ),
          )
          .toList(),
    );
  }

  List<Widget> _findingsWidgets(Map<String, dynamic> findings) {
    if (findings.isEmpty) {
      return [const Text('No findings available.')];
    }

    return findings.entries.map((entry) {
      final value = entry.value;
      final prettyValue = const JsonEncoder.withIndent('  ').convert(value);
      return ExpansionTile(
        tilePadding: EdgeInsets.zero,
        childrenPadding: const EdgeInsets.only(bottom: 12),
        title: Text(
          entry.key.replaceAll('_', ' '),
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        children: [
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(14),
              color: Colors.black.withValues(alpha: 0.18),
            ),
            child: SelectableText(
              prettyValue,
              style: const TextStyle(fontFamily: 'monospace', fontSize: 12),
            ),
          ),
        ],
      );
    }).toList();
  }

  Widget _agentSection(
    BuildContext context,
    String title,
    Map<String, dynamic> section,
  ) {
    if (_agentFailed(section)) {
      return _sectionCard(
        context,
        title,
        [
          Text(
            _agentUnavailableTitle(title),
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 8),
          Text(section['message']?.toString() ?? 'This analysis is unavailable.'),
        ],
      );
    }

    final summary = section['summary']?.toString() ?? 'No summary available.';
    final findings = Map<String, dynamic>.from(section['findings'] ?? const {});
    final recommendations = List<dynamic>.from(
      section['recommendations'] ?? const [],
    );
    final severity = section['severity']?.toString();

    return _sectionCard(
      context,
      title,
      [
        Row(
          children: [
            Expanded(
              child: Text(
                summary,
                style: Theme.of(context).textTheme.bodyLarge,
              ),
            ),
            const SizedBox(width: 12),
            _severityBadge(context, severity),
          ],
        ),
        const SizedBox(height: 16),
        Text(
          'Findings',
          style: Theme.of(
            context,
          ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700),
        ),
        const SizedBox(height: 8),
        ..._findingsWidgets(findings),
        const SizedBox(height: 12),
        Text(
          'Recommendations',
          style: Theme.of(
            context,
          ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700),
        ),
        const SizedBox(height: 8),
        _recommendationList(recommendations),
      ],
    );
  }

  Widget _stringListSection(
    BuildContext context,
    String title,
    List<String> items,
  ) {
    return _sectionCard(
      context,
      title,
      [
        if (items.isEmpty) const Text('No items available.') else _recommendationList(items),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final repoInfo = report.repositoryInfo;
    final techStack = List<String>.from(repoInfo['tech_stack'] ?? const []);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Analysis Report'),
        actions: [
          IconButton(
            tooltip: 'Copy JSON',
            icon: const Icon(Icons.copy_all_rounded),
            onPressed: () => _copyJson(context),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _sectionCard(
              context,
              'Overview',
              [
                _scoreBadge(context),
                const SizedBox(height: 16),
                _overviewRow(context, 'Repo ID', report.repoId),
                _overviewRow(context, 'Timestamp', report.timestamp),
                _overviewRow(
                  context,
                  'Project Type',
                  repoInfo['project_type']?.toString() ?? 'Unknown',
                ),
                _overviewRow(
                  context,
                  'Total Files',
                  repoInfo['total_files']?.toString() ?? '0',
                ),
                _overviewRow(
                  context,
                  'Tech Stack',
                  techStack.isEmpty ? 'Unknown' : techStack.join(', '),
                ),
              ],
            ),
            _agentSection(context, 'Summary Agent', report.summary),
            _agentSection(context, 'Judge Review', report.judgeReview),
            _agentSection(
              context,
              'Architecture Review',
              report.architectureReview,
            ),
            _agentSection(
              context,
              'Performance Review',
              report.performanceReview,
            ),
            _agentSection(context, 'Security Review', report.securityReview),
            _stringListSection(context, 'Priority Fixes', report.priorityFixes),
            _stringListSection(
              context,
              'Final Recommendations',
              report.finalRecommendations,
            ),
          ],
        ),
      ),
    );
  }
}
