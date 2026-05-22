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

  double get overallScore =>
      (report['overall_score'] as num?)?.toDouble() ?? 0.0;

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

class AnalysisProgress {
  final String status;
  final Map<String, String> steps;
  final String? message;

  AnalysisProgress({
    required this.status,
    required this.steps,
    this.message,
  });

  factory AnalysisProgress.fromJson(Map<String, dynamic> json) {
    return AnalysisProgress(
      status: json['status']?.toString() ?? 'failed',
      steps: Map<String, String>.from(json['steps'] ?? const {}),
      message: json['message']?.toString(),
    );
  }
}

class AnalysisResultPayload {
  final String status;
  final AnalysisReport? data;
  final String? message;

  AnalysisResultPayload({
    required this.status,
    this.data,
    this.message,
  });

  factory AnalysisResultPayload.fromJson(Map<String, dynamic> json) {
    final rawData = json['data'];
    return AnalysisResultPayload(
      status: json['status']?.toString() ?? 'failed',
      data: rawData is Map<String, dynamic>
          ? AnalysisReport.fromJson(rawData)
          : null,
      message: json['message']?.toString(),
    );
  }
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
      case 'not_found':
        return 'Analysis task was not found or has expired.';
      case 'failed':
        return message.isNotEmpty ? message : 'Analysis failed.';
      case 'unknown_error':
        return 'Something went wrong while generating the analysis.';
      default:
        return message.isNotEmpty ? message : 'Analysis failed.';
    }
  }

  @override
  String toString() => userMessage;
}
