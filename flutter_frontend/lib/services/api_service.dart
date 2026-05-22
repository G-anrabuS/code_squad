import 'package:dio/dio.dart';
import '../config/api_config.dart';
import '../models/analysis_report.dart';
import '../models/repo_model.dart';
import 'auth_service.dart';

class ApiService {
  final Dio _dio = Dio(
    BaseOptions(
      baseUrl: ApiConfig.baseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(minutes: 2),
    ),
  );

  final AuthService _authService = AuthService();

  Future<Options> _authOptions() async {
    final jwt = await _authService.getJwt();

    return Options(headers: {"Authorization": "Bearer $jwt"});
  }

  Future<List<RepoModel>> getRepos() async {
    final response = await _dio.get(
      "/user/repos",
      options: await _authOptions(),
    );

    return (response.data as List).map((e) => RepoModel.fromJson(e)).toList();
  }

  Future<List<String>> getBranches(String fullRepoName) async {
    final response = await _dio.get(
      "/user/branches/$fullRepoName",
      options: await _authOptions(),
    );

    return List<String>.from(response.data);
  }

  Future<String> scanRepo(String repoName, String branch) async {
    final response = await _dio.post(
      "/scan/repo",
      data: {"repo_name": repoName, "branch": branch},
      options: await _authOptions(),
    );

    return response.data["repo_path"];
  }

  Future<AnalysisReport> analyzeRepo(String repoPath) async {
    return _analyze({"repo_path": repoPath, "export_format": "json"});
  }

  Future<AnalysisReport> analyzeRepoUrl(String repoUrl) async {
    return _analyze({"repo_url": repoUrl, "export_format": "json"});
  }

  Future<String> startBackgroundAnalysis({
    String? repoPath,
    String? repoUrl,
  }) async {
    try {
      final response = await _dio.post(
        "/analysis/analyze/background",
        data: {
          if (repoPath != null) "repo_path": repoPath,
          if (repoUrl != null) "repo_url": repoUrl,
          "export_format": "json",
        },
        options: await _authOptions(),
      );

      final data = Map<String, dynamic>.from(response.data as Map);
      if (data['status']?.toString() == 'accepted' &&
          data['task_id'] != null) {
        return data['task_id'].toString();
      }

      throw AnalysisApiException(
        errorType: data['error_type']?.toString() ?? 'unknown_error',
        message:
            data['message']?.toString() ?? 'Failed to start background analysis.',
      );
    } on DioException catch (e) {
      throw _mapDioException(e);
    }
  }

  Future<AnalysisProgress> getAnalysisProgress(String taskId) async {
    try {
      final response = await _dio.get(
        "/analysis/progress/$taskId",
        options: await _authOptions(),
      );
      return AnalysisProgress.fromJson(
        Map<String, dynamic>.from(response.data as Map),
      );
    } on DioException catch (e) {
      throw _mapDioException(e);
    }
  }

  Future<AnalysisResultPayload> getAnalysisResult(String taskId) async {
    try {
      final response = await _dio.get(
        "/analysis/analysis/result/$taskId",
        options: await _authOptions(),
      );
      return AnalysisResultPayload.fromJson(
        Map<String, dynamic>.from(response.data as Map),
      );
    } on DioException catch (e) {
      throw _mapDioException(e);
    }
  }

  Future<AnalysisReport> _analyze(Map<String, dynamic> payload) async {
    try {
      final response = await _dio.post(
        "/analysis/analyze",
        data: payload,
        options: await _authOptions(),
      );

      final data = Map<String, dynamic>.from(response.data as Map);
      final status = data['status']?.toString();

      if (status == 'success') {
        return AnalysisReport.fromJson(
          Map<String, dynamic>.from(data['data'] as Map? ?? const {}),
        );
      }

      throw AnalysisApiException(
        errorType: data['error_type']?.toString() ?? 'unknown_error',
        message: data['message']?.toString() ?? 'Analysis failed.',
      );
    } on DioException catch (e) {
      throw _mapDioException(e);
    } catch (e) {
      if (e is AnalysisApiException) {
        rethrow;
      }
      throw AnalysisApiException(
        errorType: 'unknown_error',
        message: 'Analysis failed.',
      );
    }
  }

  AnalysisApiException _mapDioException(DioException e) {
    final responseData = e.response?.data;
    if (responseData is Map) {
      final data = Map<String, dynamic>.from(responseData);
      return AnalysisApiException(
        errorType: data['error_type']?.toString() ??
            data['status']?.toString() ??
            'unknown_error',
        message: data['message']?.toString() ?? 'Analysis failed.',
      );
    }

    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.receiveTimeout ||
        e.type == DioExceptionType.sendTimeout) {
      return AnalysisApiException(
        errorType: 'timeout',
        message: 'Analysis timed out.',
      );
    }

    if (e.type == DioExceptionType.connectionError ||
        e.type == DioExceptionType.unknown) {
      return AnalysisApiException(
        errorType: 'network_error',
        message: 'Network error while contacting analysis service.',
      );
    }

    return AnalysisApiException(
      errorType: 'unknown_error',
      message: 'Analysis request failed.',
    );
  }
}
