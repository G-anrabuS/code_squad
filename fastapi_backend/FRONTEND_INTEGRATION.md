"""
Integration Guide - How Frontend Can Use Analysis API
"""

# ============================================================================
# FRONTEND INTEGRATION WITH ANALYSIS BACKEND
# ============================================================================

# The frontend can trigger analysis in two ways:

# 1. VIA REST API (Recommended for Flutter/Web)
# ==============================================

// In your Flutter app (example):
import 'package:http/http.dart' as http;
import 'dart:convert';

class AnalysisService {
  final String backendUrl = 'http://localhost:8000';

  // Get repository path from user selection, then analyze
  Future<Map<String, dynamic>> analyzeRepository(String repoPath) async {
    try {
      final response = await http.post(
        Uri.parse('$backendUrl/analysis/analyze'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'repo_path': repoPath,
          'export_format': 'json',
        }),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Analysis failed: ${response.body}');
      }
    } catch (e) {
      throw Exception('Error: $e');
    }
  }

  // For large repos, use background analysis
  Future<String> analyzeRepositoryBackground(String repoPath) async {
    try {
      final response = await http.post(
        Uri.parse('$backendUrl/analysis/analyze/background'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'repo_path': repoPath,
          'export_format': 'json',
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['task_id']; // Return task ID to check later
      } else {
        throw Exception('Analysis failed');
      }
    } catch (e) {
      throw Exception('Error: $e');
    }
  }

  // Poll for results
  Future<Map<String, dynamic>> getAnalysisResult(String taskId) async {
    try {
      final response = await http.get(
        Uri.parse('$backendUrl/analysis/result/$taskId'),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get results');
      }
    } catch (e) {
      throw Exception('Error: $e');
    }
  }

  // Get quick summary
  Future<Map<String, dynamic>> getAnalysisSummary(String taskId) async {
    try {
      final response = await http.get(
        Uri.parse('$backendUrl/analysis/summary/$taskId'),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get summary');
      }
    } catch (e) {
      throw Exception('Error: $e');
    }
  }
}

// Usage in Flutter screen:
class AnalysisScreen extends StatefulWidget {
  @override
  State<AnalysisScreen> createState() => _AnalysisScreenState();
}

class _AnalysisScreenState extends State<AnalysisScreen> {
  final analysisService = AnalysisService();
  String? selectedRepo;
  String? taskId;
  bool isLoading = false;
  Map<String, dynamic>? analysisResult;

  Future<void> startAnalysis() async {
    if (selectedRepo == null) return;

    setState(() => isLoading = true);

    try {
      // Use background analysis for large repos
      taskId = await analysisService.analyzeRepositoryBackground(selectedRepo!);
      
      // Poll for results
      await pollForResults();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: ${e.toString()}')),
      );
    } finally {
      setState(() => isLoading = false);
    }
  }

  Future<void> pollForResults() async {
    if (taskId == null) return;

    // Poll every 2 seconds
    while (true) {
      await Future.delayed(Duration(seconds: 2));
      
      final result = await analysisService.getAnalysisResult(taskId!);
      
      if (result['status'] == 'complete') {
        setState(() => analysisResult = result);
        break;
      } else if (result['status'] == 'error') {
        throw Exception(result['error']);
      }
      // If still processing, continue polling
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Repository Analysis')),
      body: Column(
        children: [
          // Repo selection button
          ElevatedButton(
            onPressed: selectRepository,
            child: Text('Select Repository'),
          ),
          if (selectedRepo != null)
            Text('Selected: $selectedRepo'),
          
          // Analysis button
          if (selectedRepo != null && !isLoading)
            ElevatedButton(
              onPressed: startAnalysis,
              child: Text('Start Analysis'),
            ),
          
          if (isLoading)
            CircularProgressIndicator(),
          
          // Results display
          if (analysisResult != null)
            ResultsWidget(result: analysisResult!),
        ],
      ),
    );
  }

  void selectRepository() async {
    // Use file picker to select repo directory
    final path = await FilePicker.platform.getDirectoryPath();
    if (path != null) {
      setState(() => selectedRepo = path);
    }
  }
}

class ResultsWidget extends StatelessWidget {
  final Map<String, dynamic> result;

  const ResultsWidget({required this.result});

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Code Quality: ${_getQualityScore()}'),
            Text('Security Level: ${_getSecurityLevel()}'),
            SizedBox(height: 16),
            Text('Priority Actions:', style: TextStyle(fontWeight: FontWeight.bold)),
            ..._getPriorityActions().map((action) => Padding(
              padding: EdgeInsets.all(8),
              child: Text('• $action'),
            )),
          ],
        ),
      ),
    );
  }

  String _getQualityScore() {
    final report = result['report'] as Map<String, dynamic>;
    final score = report['code_quality_assessment']['overall_score'] as double;
    return '${(score * 100).toStringAsFixed(0)}%';
  }

  String _getSecurityLevel() {
    final report = result['report'] as Map<String, dynamic>;
    return report['security_assessment']['severity_level'].toString();
  }

  List<String> _getPriorityActions() {
    final report = result['report'] as Map<String, dynamic>;
    return List<String>.from(report['priority_actions'] ?? []);
  }
}


# 2. WORKFLOW EXAMPLE
# ===================

# User Journey:
1. Opens Repository Selection Screen
   ↓
2. Selects local repository folder
   ↓
3. Clicks "Analyze Repository"
   ↓
4. Shows "Analysis in Progress..." with loading spinner
   ↓
5. Backend:
   - Parses codebase (agent 1)
   - Generates summary (agent 2)
   - Reviews code quality (agent 3)
   - Analyzes architecture (agent 4)
   - Checks performance (agent 5)
   - Scans security (agent 6)
   - Generates report (agent 7)
   ↓
6. Frontend receives report and displays:
   - Project Type
   - Tech Stack
   - Code Quality Score
   - Security Level
   - Priority Actions
   - Full Details Tab
   ↓
7. User can:
   - View full report
   - Export as PDF/Markdown
   - Share results
   - Save for comparison


# 3. UI MOCKUP
# ============

┌─────────────────────────────────────────┐
│  CodeSquad Analysis                  [>]│
├─────────────────────────────────────────┤
│                                         │
│  📂 Select Repository                   │
│  [Browse Folder...]                     │
│  Selected: /path/to/my/project          │
│                                         │
│  [🔍 Analyze]  [📊 Recent]              │
│                                         │
├─────────────────────────────────────────┤
│ ⏳ Analysis in progress... (45%)        │
│ • Parsing codebase ✓                   │
│ • Analyzing code quality ⏳             │
│ • Checking security                    │
│                                         │
├─────────────────────────────────────────┤
│ Results:                                │
│                                         │
│ 📊 Code Quality: ████████░░ 72%        │
│ 🔒 Security: MEDIUM (3 issues)         │
│ ⚡ Performance: 8 bottlenecks found    │
│ 🏗️  Architecture: Moderate complexity  │
│                                         │
│ 🎯 Priority Actions:                    │
│ 1. Fix hardcoded secrets                │
│ 2. Add input validation                 │
│ 3. Optimize N+1 queries                 │
│ 4. Refactor large files                 │
│ 5. Add tests                            │
│                                         │
│ [📋 Details] [📄 Export] [💾 Save]     │
│                                         │
└─────────────────────────────────────────┘


# 4. RESPONSE FORMATS
# ===================

## Quick Summary Response:
{
  "status": "complete",
  "repository_info": {
    "total_files": 45,
    "project_type": "Backend API",
    "tech_stack": ["Python", "FastAPI"]
  },
  "code_quality_score": 0.72,
  "security_level": "MEDIUM",
  "priority_actions": [
    "🔴 CRITICAL: Fix secrets",
    "🔴 HIGH: Add validation",
    "🟠 PERFORMANCE: Optimize queries"
  ]
}

## Full Report Response:
{
  "status": "complete",
  "report": {
    "timestamp": "2024-01-15T10:30:00",
    "repository_info": { ... },
    "project_summary": { ... },
    "architecture_analysis": { ... },
    "code_quality_assessment": { ... },
    "performance_analysis": { ... },
    "security_assessment": { ... },
    "recommendations": { ... },
    "priority_actions": [ ... ]
  }
}


# 5. ERROR HANDLING
# =================

try {
  // Start analysis
  taskId = await analysisService.analyzeRepositoryBackground(repoPath);
  
  // Poll for results
  while (true) {
    final result = await analysisService.getAnalysisResult(taskId);
    
    if (result['status'] == 'error') {
      // Handle error
      print('Analysis failed: ${result['error']}');
      rethrow;
    }
    
    if (result['status'] == 'complete') {
      // Process results
      return result['report'];
    }
    
    // Still processing, wait and retry
    await Future.delayed(Duration(seconds: 2));
  }
} catch (e) {
  // Show error to user
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(content: Text('Error: ${e.toString()}')),
  );
}


# 6. STATE MANAGEMENT (Using Provider)
# =====================================

class AnalysisProvider with ChangeNotifier {
  String? _selectedRepo;
  String? _taskId;
  Map<String, dynamic>? _report;
  bool _isLoading = false;
  String? _error;

  String? get selectedRepo => _selectedRepo;
  String? get taskId => _taskId;
  Map<String, dynamic>? get report => _report;
  bool get isLoading => _isLoading;
  String? get error => _error;

  final _analysisService = AnalysisService();

  Future<void> selectRepository(String path) async {
    _selectedRepo = path;
    notifyListeners();
  }

  Future<void> startAnalysis() async {
    if (_selectedRepo == null) return;
    
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _taskId = await _analysisService.analyzeRepositoryBackground(_selectedRepo!);
      await _pollForResults();
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> _pollForResults() async {
    if (_taskId == null) return;

    while (true) {
      await Future.delayed(Duration(seconds: 2));
      
      try {
        final result = await _analysisService.getAnalysisResult(_taskId!);
        
        if (result['status'] == 'complete') {
          _report = result['report'];
          notifyListeners();
          break;
        } else if (result['status'] == 'error') {
          _error = result['error'];
          notifyListeners();
          break;
        }
      } catch (e) {
        _error = e.toString();
        notifyListeners();
      }
    }
  }
}


# 7. FUTURE ENHANCEMENTS
# ======================

- [ ] Export analysis as PDF report
- [ ] Compare multiple repositories
- [ ] Track analysis history
- [ ] Custom rule configuration
- [ ] Team collaboration/sharing
- [ ] Integration with GitHub/GitLab
- [ ] Automated periodic scans
- [ ] Trend analysis over time
- [ ] AI-powered fix recommendations
- [ ] One-click auto-fix for common issues

