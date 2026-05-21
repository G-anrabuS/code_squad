import 'package:flutter/material.dart';

class BranchScreen extends StatelessWidget {
  final String jwt;
  final String repoName;

  const BranchScreen({super.key, required this.jwt, required this.repoName});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(repoName)),
      body: const Center(child: Text("Branch screen coming next")),
    );
  }
}
