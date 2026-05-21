class RepoModel {
  final String name;
  final bool isPrivate;

  RepoModel({required this.name, required this.isPrivate});

  factory RepoModel.fromJson(Map<String, dynamic> json) {
    return RepoModel(name: json["name"], isPrivate: json["private"] ?? false);
  }
}
