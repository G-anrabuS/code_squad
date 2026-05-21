class RepoModel {
  final String name;
  final String fullName;
  final bool isPrivate;

  RepoModel({
    required this.name,
    required this.fullName,
    required this.isPrivate,
  });

  factory RepoModel.fromJson(Map<String, dynamic> json) {
    return RepoModel(
      name: json["name"],
      fullName: json["full_name"],
      isPrivate: json["private"] ?? false,
    );
  }
}
