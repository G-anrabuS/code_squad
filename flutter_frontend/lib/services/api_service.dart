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
      final responseData = e.response?.data;
      if (responseData is Map) {
        final data = Map<String, dynamic>.from(responseData);
        throw AnalysisApiException(
          errorType: data['error_type']?.toString() ?? 'unknown_error',
          message: data['message']?.toString() ?? 'Analysis failed.',
        );
      }

      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.sendTimeout) {
        throw AnalysisApiException(
          errorType: 'timeout',
          message: 'Analysis timed out.',
        );
      }

      if (e.type == DioExceptionType.connectionError ||
          e.type == DioExceptionType.unknown) {
        throw AnalysisApiException(
          errorType: 'network_error',
          message: 'Network error while contacting analysis service.',
        );
      }
      throw AnalysisApiException(
        errorType: 'unknown_error',
        message: 'Analysis request failed.',
      );
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
}
