import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../widgets/app_feedback.dart';
import 'scan_screen.dart';

class BranchScreen extends StatefulWidget {
  final String repoName;

  const BranchScreen({super.key, required this.repoName});

  @override
  State<BranchScreen> createState() => _BranchScreenState();
}

class _BranchScreenState extends State<BranchScreen> {
  final ApiService _apiService = ApiService();

  List<String> branches = [];
  bool loading = true;

  @override
  void initState() {
    super.initState();
    _loadBranches();
  }

  Future<void> _loadBranches() async {
    try {
      branches = await _apiService.getBranches(widget.repoName);
    } catch (e) {
      if (!mounted) return;
      showErrorSnackBar(context, "Failed to load branches: $e");
    } finally {
      if (mounted) {
        setState(() => loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.repoName)),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: branches.length,
              itemBuilder: (context, index) {
                final branch = branches[index];

                return Card(
                  margin: const EdgeInsets.all(8),
                  child: ListTile(
                    title: Text(branch),
                    trailing: const Icon(Icons.arrow_forward_ios),
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => ScanScreen(
                            repoName: widget.repoName,
                            branchName: branch,
                          ),
                        ),
                      );
                    },
                  ),
                );
              },
            ),
    );
  }
}
