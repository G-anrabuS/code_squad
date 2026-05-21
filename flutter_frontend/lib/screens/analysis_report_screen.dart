import 'package:flutter/material.dart';
import '../models/analysis_report.dart';

class AnalysisReportScreen extends StatelessWidget {
  final AnalysisReport report;

  const AnalysisReportScreen({super.key, required this.report});

  Widget sectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Text(
        title,
        style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
      ),
    );
  }

  Widget infoCard(String title, String value) {
    return Card(
      child: ListTile(title: Text(title), subtitle: Text(value)),
    );
  }

  Widget listCard(String title, List<dynamic> items) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 10),
            ...items
                .take(5)
                .map(
                  (e) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Text("• $e"),
                  ),
                ),
          ],
        ),
      ),
    );
  }

  Widget scoreCard(String title, double score) {
    return Card(
      child: ListTile(
        title: Text(title),
        trailing: Text("${(score * 100).toInt()}%"),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final repoInfo = report.repositoryInfo;
    final summary = report.projectSummary;
    final architecture = report.architectureAnalysis;
    final quality = report.codeQuality;
    final performance = report.performance;
    final security = report.security;
    final recommendations = report.recommendations;

    return Scaffold(
      appBar: AppBar(title: const Text("Analysis Report")),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            sectionTitle("Project Overview"),

            infoCard(
              "Project Type",
              repoInfo["project_type"]?.toString() ?? "Unknown",
            ),

            infoCard(
              "Tech Stack",
              (repoInfo["tech_stack"] as List?)?.join(", ") ?? "Unknown",
            ),

            infoCard("Total Files", repoInfo["total_files"]?.toString() ?? "0"),

            sectionTitle("Architecture"),

            infoCard(
              "Pattern",
              architecture["current_pattern"]?.toString() ?? "Unknown",
            ),

            infoCard(
              "Maturity",
              architecture["maturity"]?.toString() ?? "Unknown",
            ),

            infoCard(
              "Complexity",
              architecture["complexity"]?.toString() ?? "Unknown",
            ),

            sectionTitle("Code Quality"),

            scoreCard(
              "Maintainability",
              (quality["maintainability"] ?? 0).toDouble(),
            ),

            scoreCard("Scalability", (quality["scalability"] ?? 0).toDouble()),

            scoreCard("Readability", (quality["readability"] ?? 0).toDouble()),

            scoreCard("Modularity", (quality["modularity"] ?? 0).toDouble()),

            sectionTitle("Security"),

            infoCard(
              "Severity",
              security["severity_level"]?.toString() ?? "Unknown",
            ),

            listCard("High Risk Issues", security["high_risk_issues"] ?? []),

            listCard(
              "Medium Risk Issues",
              security["medium_risk_issues"] ?? [],
            ),

            sectionTitle("Performance"),

            listCard("Priority Fixes", performance["priority_fixes"] ?? []),

            listCard(
              "Caching Opportunities",
              performance["caching_opportunities"] ?? [],
            ),

            sectionTitle("Recommendations"),

            listCard(
              "Architecture Improvements",
              recommendations["architecture_improvements"] ?? [],
            ),

            listCard("Security Fixes", recommendations["security_fixes"] ?? []),

            sectionTitle("Priority Actions"),

            listCard("Immediate Actions", report.priorityActions),
          ],
        ),
      ),
    );
  }
}
