class AnalysisReport {
  final Map<String, dynamic> raw;

  AnalysisReport({required this.raw});

  factory AnalysisReport.fromJson(Map<String, dynamic> json) {
    return AnalysisReport(raw: json);
  }

  Map<String, dynamic> get report => raw;

  String get repoId => report['repo_id']?.toString() ?? '';
  String get timestamp => report['timestamp']?.toString() ?? '';

  Map<String, dynamic> get repositoryInfo =>
      Map<String, dynamic>.from(report['repository_info'] ?? const {});

  Map<String, dynamic> get repoContext =>
      Map<String, dynamic>.from(report['repo_context'] ?? const {});

  double get overallScore => (report['overall_score'] as num?)?.toDouble() ?? 0.0;

  Map<String, dynamic> get summary =>
      Map<String, dynamic>.from(report['summary'] ?? const {});

  Map<String, dynamic> get judgeReview =>
      Map<String, dynamic>.from(report['judge_review'] ?? const {});

  Map<String, dynamic> get architectureReview =>
      Map<String, dynamic>.from(report['architecture_review'] ?? const {});

  Map<String, dynamic> get performanceReview =>
      Map<String, dynamic>.from(report['performance_review'] ?? const {});

  Map<String, dynamic> get securityReview =>
      Map<String, dynamic>.from(report['security_review'] ?? const {});

  List<String> get priorityFixes =>
      List<String>.from(report['priority_fixes'] ?? const []);

  List<String> get finalRecommendations =>
      List<String>.from(report['final_recommendations'] ?? const []);
}

class AnalysisApiException implements Exception {
  final String errorType;
  final String message;

  AnalysisApiException({
    required this.errorType,
    required this.message,
  });

  String get userMessage {
    switch (errorType) {
      case 'quota_exceeded':
        return 'AI analysis quota exceeded. Please try again later.';
      case 'invalid_api_key':
        return 'Analysis service is not configured correctly.';
      case 'timeout':
        return 'Analysis timed out. Please retry.';
      case 'network_error':
        return 'Network error while contacting analysis service.';
      case 'parsing_error':
        return 'Analysis service returned an unreadable response.';
      case 'analysis_failed':
        return 'Analysis could not be completed. Please try again.';
      case 'unknown_error':
        return 'Something went wrong while generating the analysis.';
      default:
        return message.isNotEmpty ? message : 'Analysis failed.';
    }
  }

  @override
  String toString() => userMessage;
}
