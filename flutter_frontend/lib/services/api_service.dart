import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../config/api_config.dart';
import '../models/repo_model.dart';
import '../models/analysis_report.dart';
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
    final response = await _dio.post(
      "/analysis/analyze",
      data: {"repo_path": repoPath, "export_format": "json"},
      options: await _authOptions(),
    );

    final data = response.data as Map<String, dynamic>;
    if (data['status'] != 'success') {
      debugPrint('API analyzeRepo error: ${data['error']}');
      throw Exception(data['error'] ?? 'Analysis failed');
    }

    return AnalysisReport.fromJson(data['report'] as Map<String, dynamic>);
  }

  Future<AnalysisReport> analyzeRepoUrl(String repoUrl) async {
    final response = await _dio.post(
      "/analysis/analyze",
      data: {"repo_url": repoUrl, "export_format": "json"},
      options: await _authOptions(),
    );

    final data = response.data as Map<String, dynamic>;
    if (data['status'] != 'success') {
      debugPrint('API analyzeRepoUrl error: ${data['error']}');
      throw Exception(data['error'] ?? 'Analysis failed');
    }

    return AnalysisReport.fromJson(data['report'] as Map<String, dynamic>);
  }
}
