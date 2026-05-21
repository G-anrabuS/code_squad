class AnalysisReport {
  final Map<String, dynamic> raw;

  AnalysisReport({required this.raw});

  factory AnalysisReport.fromJson(Map<String, dynamic> json) {
    return AnalysisReport(raw: json);
  }

  Map<String, dynamic> get report => raw["report"] ?? {};

  Map<String, dynamic> get repositoryInfo => report["repository_info"] ?? {};

  Map<String, dynamic> get projectSummary => report["project_summary"] ?? {};

  Map<String, dynamic> get architectureAnalysis =>
      report["architecture_analysis"] ?? {};

  Map<String, dynamic> get codeQuality =>
      report["code_quality_assessment"] ?? {};

  Map<String, dynamic> get performance => report["performance_analysis"] ?? {};

  Map<String, dynamic> get security => report["security_assessment"] ?? {};

  Map<String, dynamic> get recommendations => report["recommendations"] ?? {};

  List<dynamic> get priorityActions => report["priority_actions"] ?? [];
}
