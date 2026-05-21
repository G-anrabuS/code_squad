import 'package:dio/dio.dart';
import '../config/api_config.dart';

class ApiService {
  final Dio dio = Dio();

  Future<List<dynamic>> fetchRepos(String jwt) async {
    final response = await dio.get(
      "${ApiConfig.baseUrl}/user/repos",
      options: Options(headers: {"Authorization": "Bearer $jwt"}),
    );

    return response.data;
  }

  Future<List<dynamic>> fetchBranches(String repoName, String jwt) async {
    final response = await dio.get(
      "${ApiConfig.baseUrl}/user/branches/$repoName",
      options: Options(headers: {"Authorization": "Bearer $jwt"}),
    );

    return response.data;
  }

  Future<Map<String, dynamic>> scanRepo(
    String repoName,
    String branch,
    String jwt,
  ) async {
    final response = await dio.post(
      "${ApiConfig.baseUrl}/scan/repo",
      data: {"repo_name": repoName, "branch": branch},
      options: Options(headers: {"Authorization": "Bearer $jwt"}),
    );

    return response.data;
  }
}
