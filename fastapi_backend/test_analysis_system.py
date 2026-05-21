"""
Test Script - Verify Analysis System Works
Run this after starting the backend server
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.analysis_pipeline import AnalysisPipeline
from app.services.report_generator import ReportGenerator


async def test_full_analysis():
    """Test the full analysis pipeline."""
    
    print("=" * 70)
    print("🧪 TESTING CODEBASE ANALYSIS SYSTEM")
    print("=" * 70)
    
    # Initialize pipeline
    pipeline = AnalysisPipeline()
    
    # Test 1: Analyze backend
    print("\n✅ Test 1: Analyzing FastAPI Backend...")
    backend_path = Path(__file__).parent
    
    try:
        report = await pipeline.analyze_repository(str(backend_path))
        print("   ✓ Backend analysis completed")
        print(f"   - Total files: {report.repository_info['total_files']}")
        print(f"   - Project type: {report.repository_info['project_type']}")
        print(f"   - Tech stack: {', '.join(report.repository_info['tech_stack'])}")
        print(f"   - Code quality: {report.code_quality_assessment['overall_score']:.0%}")
        print(f"   - Security level: {report.security_assessment['severity_level']}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 2: Export as Markdown
    print("\n✅ Test 2: Exporting as Markdown...")
    try:
        generator = ReportGenerator()
        markdown = generator.to_markdown(report)
        
        # Save to file
        report_file = backend_path / "test_report.md"
        with open(report_file, "w") as f:
            f.write(markdown)
        
        print(f"   ✓ Markdown report exported")
        print(f"   - File size: {len(markdown)} characters")
        print(f"   - Saved to: {report_file}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 3: Export as JSON
    print("\n✅ Test 3: Exporting as JSON...")
    try:
        json_data = generator.to_dict(report)
        
        # Save to file
        import json
        json_file = backend_path / "test_report.json"
        with open(json_file, "w") as f:
            json.dump(json_data, f, indent=2)
        
        print(f"   ✓ JSON report exported")
        print(f"   - Keys in report: {len(json_data.keys())}")
        print(f"   - Saved to: {json_file}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 4: Display summary
    print("\n✅ Test 4: Analysis Summary")
    print("   -" * 35)
    
    print("\n   📊 REPOSITORY INFO:")
    print(f"   • Total Files: {report.repository_info['total_files']}")
    print(f"   • Project Type: {report.repository_info['project_type']}")
    print(f"   • Tech Stack: {', '.join(report.repository_info['tech_stack'])}")
    print(f"   • Important Files: {len(report.repository_info['important_files'])}")
    
    print("\n   💻 CODE QUALITY:")
    quality = report.code_quality_assessment
    print(f"   • Overall Score: {quality['overall_score']:.0%}")
    print(f"   • Maintainability: {quality['maintainability']:.0%}")
    print(f"   • Scalability: {quality['scalability']:.0%}")
    print(f"   • Technical Debt Items: {len(quality['technical_debt'])}")
    
    print("\n   🏗️  ARCHITECTURE:")
    arch = report.architecture_analysis
    print(f"   • Current Pattern: {arch['current_pattern']}")
    print(f"   • Maturity: {arch['maturity']}")
    print(f"   • Complexity: {arch['complexity']}")
    print(f"   • Refactoring Opportunities: {len(arch['refactoring_opportunities'])}")
    
    print("\n   ⚡ PERFORMANCE:")
    perf = report.performance_analysis
    print(f"   • Bottlenecks Found: {len(perf['bottlenecks'])}")
    print(f"   • Async Score: {perf['async_handling_score']:.0%}")
    print(f"   • Caching Opportunities: {len(perf['caching_opportunities'])}")
    print(f"   • Priority Fixes: {len(perf['priority_fixes'])}")
    
    print("\n   🔒 SECURITY:")
    sec = report.security_assessment
    print(f"   • Severity Level: {sec['severity_level']}")
    print(f"   • Critical Issues: {len(sec['critical_vulnerabilities'])}")
    print(f"   • High Risk Issues: {len(sec['high_risk_issues'])}")
    print(f"   • API Security Score: {sec['api_security_score']:.0%}")
    
    print("\n   🎯 PRIORITY ACTIONS:")
    for i, action in enumerate(report.priority_actions[:5], 1):
        print(f"   {i}. {action}")
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED")
    print("=" * 70)
    print("\n📁 Generated Files:")
    print(f"   • {report_file}")
    print(f"   • {json_file}")
    print("\n💡 Next Steps:")
    print("   1. Review the generated test reports")
    print("   2. Try analyzing different repositories")
    print("   3. Test via REST API endpoints")
    print("   4. Integrate with Flutter frontend")
    print("\n")
    
    return True


async def test_agents_independently():
    """Test each agent independently."""
    
    print("\n" + "=" * 70)
    print("🧪 TESTING INDIVIDUAL AGENTS")
    print("=" * 70)
    
    from app.services.codebase_parser import CodebaseParser
    from app.agents import (
        CodebaseAnalyzerAgent, SummaryAgent, JudgeAgent,
        ArchitectAgent, PerformanceAgent, SecurityAgent
    )
    
    backend_path = str(Path(__file__).parent)
    
    # Parse codebase first
    print("\n📂 Parsing codebase...")
    parser = CodebaseParser(backend_path)
    codebase_data = parser.parse()
    
    agents = {
        'Codebase Analyzer': CodebaseAnalyzerAgent(),
        'Summary': SummaryAgent(),
        'Judge': JudgeAgent(),
        'Architect': ArchitectAgent(),
        'Performance': PerformanceAgent(),
        'Security': SecurityAgent(),
    }
    
    for agent_name, agent in agents.items():
        print(f"\n🤖 Testing {agent_name}...")
        try:
            response = await agent.analyze(codebase_data)
            print(f"   ✓ {agent_name} agent working")
            print(f"   - Findings: {len(response.findings)} keys")
            print(f"   - Recommendations: {len(response.recommendations)}")
            if response.severity:
                print(f"   - Severity: {response.severity}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False
    
    print("\n" + "=" * 70)
    print("✅ ALL AGENTS TESTED SUCCESSFULLY")
    print("=" * 70 + "\n")
    
    return True


async def main():
    """Run all tests."""
    
    try:
        # Test individual agents
        success1 = await test_agents_independently()
        
        # Test full pipeline
        success2 = await test_full_analysis()
        
        if success1 and success2:
            print("\n🎉 ALL TESTS PASSED - SYSTEM READY!")
            return True
        else:
            print("\n❌ SOME TESTS FAILED")
            return False
    
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
