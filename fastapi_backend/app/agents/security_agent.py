"""
Security Agent - Scans for security vulnerabilities and suggests improvements.
"""
from typing import Dict, Any, List, Tuple
from app.agents.base_agent import BaseAnalysisAgent, AgentResponse


class SecurityAgent(BaseAnalysisAgent):
    """Analyzes codebase for security vulnerabilities."""
    
    def __init__(self):
        super().__init__("Security Agent")
        
    async def analyze(self, codebase_data: Dict[str, Any]) -> AgentResponse:
        """Analyze codebase for security issues."""
        
        findings = {
            'critical_vulnerabilities': self._find_critical_vulnerabilities(codebase_data),
            'high_risk_issues': self._find_high_risk_issues(codebase_data),
            'medium_risk_issues': self._find_medium_risk_issues(codebase_data),
            'dependency_risks': self._assess_dependency_risks(codebase_data),
            'authentication_issues': self._check_authentication(codebase_data),
            'api_security': self._assess_api_security(codebase_data),
            'data_handling': self._assess_data_handling(codebase_data),
            'compliance_risks': self._identify_compliance_risks(codebase_data),
            'security_recommendations': self._generate_security_recommendations(codebase_data),
        }
        
        critical_count = len(findings['critical_vulnerabilities'])
        high_count = len(findings['high_risk_issues'])
        
        summary = f"""
        SECURITY ANALYSIS:
        
        ⚠️  CRITICAL Issues: {critical_count}
        🔴 HIGH Risk Issues: {high_count}
        🟡 MEDIUM Risk Issues: {len(findings['medium_risk_issues'])}
        
        Authentication: {'✓ Detected' if findings['authentication_issues'] else '⚠️  Review needed'}
        API Security: {findings['api_security'].get('score', 0):.0%}
        Dependency Risks: {len(findings['dependency_risks'])}
        
        Top Priority: {findings['critical_vulnerabilities'][0] if findings['critical_vulnerabilities'] else 'No critical issues'}
        """
        
        severity = 'CRITICAL' if critical_count > 0 else ('HIGH' if high_count > 0 else 'MEDIUM')
        recommendations = self._generate_security_fixes(findings)
        
        return self.format_findings(findings, summary.strip(), recommendations, severity)
    
    def _find_critical_vulnerabilities(self, codebase_data: Dict[str, Any]) -> List[str]:
        """Find critical security vulnerabilities."""
        vulnerabilities = []
        
        important_files = codebase_data.get('important_files', [])
        
        # Check for hardcoded secrets
        if any('secret' in f.lower() or 'password' in f.lower() or 'api_key' in f.lower() or 'token' in f.lower() for f in important_files):
            # If in non-config file, it's critical
            if not any('config' in f.lower() or 'env' in f.lower() for f in important_files if 'secret' in f.lower()):
                vulnerabilities.append("CRITICAL: Hardcoded secrets/API keys detected in source code")
        
        # Check for SQL injection risks
        if any('sql' in f.lower() or 'query' in f.lower() or 'database' in f.lower() for f in important_files):
            vulnerabilities.append("CRITICAL: Potential SQL injection risks - verify parameterized queries")
        
        # Check for authentication bypass
        if any('auth' in f.lower() for f in important_files):
            vulnerabilities.append("CRITICAL: Review authentication implementation for bypass vulnerabilities")
        
        return vulnerabilities
    
    def _find_high_risk_issues(self, codebase_data: Dict[str, Any]) -> List[str]:
        """Find high-risk security issues."""
        issues = []
        
        important_files = codebase_data.get('important_files', [])
        tech_stack = codebase_data.get('tech_stack', [])
        
        # Check for authentication
        has_auth = any('auth' in f.lower() for f in important_files)
        if not has_auth and any(t in tech_stack for t in ['FastAPI', 'Django']):
            issues.append("HIGH: No authentication mechanism detected in API")
        
        # Check for authorization
        has_permission = any('permission' in f.lower() or 'role' in f.lower() for f in important_files)
        if not has_permission:
            issues.append("HIGH: No authorization/permission system detected")
        
        # Check for input validation
        has_validation = any('validation' in f.lower() or 'validator' in f.lower() or 'pydantic' in str(tech_stack).lower() for f in important_files)
        if not has_validation and any(t in tech_stack for t in ['FastAPI', 'Django']):
            issues.append("HIGH: Missing input validation - risk of injection attacks")
        
        # Check for CORS configuration
        if any(t in tech_stack for t in ['FastAPI', 'Django', 'React']):
            has_cors = any('cors' in f.lower() for f in important_files)
            if not has_cors:
                issues.append("HIGH: CORS configuration not explicitly set - may expose API")
        
        # Check for HTTPS
        issues.append("HIGH: Verify HTTPS/TLS is enforced in production")
        
        # Check for secure headers
        if any(t in tech_stack for t in ['React', 'Vue', 'Angular']):
            issues.append("HIGH: Configure Security Headers (CSP, X-Frame-Options, etc.)")
        
        return issues
    
    def _find_medium_risk_issues(self, codebase_data: Dict[str, Any]) -> List[str]:
        """Find medium-risk security issues."""
        issues = []
        
        important_files = codebase_data.get('important_files', [])
        dependencies = codebase_data.get('dependencies', {})
        
        # Check for logging
        has_logging = any('logging' in f.lower() or 'logger' in f.lower() for f in important_files)
        if not has_logging:
            issues.append("MEDIUM: No logging infrastructure - reduces audit trail")
        
        # Check for error handling
        has_error_handling = any('error' in f.lower() or 'exception' in f.lower() for f in important_files)
        if not has_error_handling:
            issues.append("MEDIUM: Missing error handling - may leak information")
        
        # Check for rate limiting
        if any('api' in f.lower() for f in important_files):
            if not any('rate' in f.lower() or 'throttle' in f.lower() for f in important_files):
                issues.append("MEDIUM: No rate limiting - vulnerable to brute force attacks")
        
        # Dependency security
        all_deps = []
        for dep_list in dependencies.values():
            all_deps.extend(dep_list)
        
        if len(all_deps) == 0:
            issues.append("MEDIUM: No dependency management system detected")
        
        return issues
    
    def _assess_dependency_risks(self, codebase_data: Dict[str, Any]) -> List[str]:
        """Assess risks from dependencies."""
        risks = []
        
        dependencies = codebase_data.get('dependencies', {})
        all_deps = []
        for dep_list in dependencies.values():
            all_deps.extend(dep_list)
        
        if len(all_deps) > 50:
            risks.append("HIGH: Large number of dependencies increases attack surface")
        
        # Known vulnerable package checks (simplified)
        risky_packages = ['moment.js', 'lodash', 'serialize-javascript']
        for pkg in risky_packages:
            if any(pkg in d.lower() for d in all_deps):
                risks.append(f"Review {pkg} for known vulnerabilities")
        
        if len(all_deps) > 0:
            risks.append("Run 'npm audit' / 'pip audit' to check for vulnerable versions")
        
        return risks
    
    def _check_authentication(self, codebase_data: Dict[str, Any]) -> List[str]:
        """Check authentication mechanisms."""
        auth_findings = []
        
        important_files = codebase_data.get('important_files', [])
        
        # Check what auth methods are used
        if any('jwt' in f.lower() for f in important_files):
            auth_findings.append("JWT-based authentication")
        
        if any('oauth' in f.lower() or 'github' in f.lower() for f in important_files):
            auth_findings.append("OAuth/Social authentication")
        
        if any('session' in f.lower() for f in important_files):
            auth_findings.append("Session-based authentication")
        
        if any('password' in f.lower() or 'hash' in f.lower() for f in important_files):
            auth_findings.append("Password-based authentication")
        
        return auth_findings
    
    def _assess_api_security(self, codebase_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess API security."""
        important_files = codebase_data.get('important_files', [])
        tech_stack = codebase_data.get('tech_stack', [])
        
        has_auth = any('auth' in f.lower() for f in important_files)
        has_validation = any('validation' in f.lower() or 'pydantic' in str(tech_stack).lower() for f in important_files)
        has_error_handling = any('error' in f.lower() or 'exception' in f.lower() for f in important_files)
        has_api = any(t in tech_stack for t in ['FastAPI', 'Django', 'Spring'])
        
        score = (int(has_auth) + int(has_validation) + int(has_error_handling)) / 3 if has_api else 0
        
        return {
            'score': score,
            'has_authentication': has_auth,
            'has_input_validation': has_validation,
            'has_error_handling': has_error_handling,
            'issues': [
                "Missing authentication" if not has_auth else None,
                "Missing validation" if not has_validation else None,
                "Poor error handling" if not has_error_handling else None,
            ]
        }
    
    def _assess_data_handling(self, codebase_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess how sensitive data is handled."""
        important_files = codebase_data.get('important_files', [])
        
        issues = []
        
        # Check for encryption
        has_encryption = any('encrypt' in f.lower() or 'crypto' in f.lower() for f in important_files)
        if not has_encryption:
            issues.append("No encryption detected - verify sensitive data protection")
        
        # Check for data masking
        has_masking = any('mask' in f.lower() or 'redact' in f.lower() for f in important_files)
        if not has_masking:
            issues.append("No data masking in logs/responses")
        
        # Check for GDPR compliance
        has_data_deletion = any('delete' in f.lower() or 'purge' in f.lower() for f in important_files)
        if not has_data_deletion:
            issues.append("No data retention/deletion policy detected")
        
        return {
            'has_encryption': has_encryption,
            'has_masking': has_masking,
            'has_data_deletion': has_data_deletion,
            'issues': issues
        }
    
    def _identify_compliance_risks(self, codebase_data: Dict[str, Any]) -> List[str]:
        """Identify compliance-related risks."""
        risks = []
        
        important_files = codebase_data.get('important_files', [])
        
        # GDPR
        risks.append("GDPR: Ensure data privacy and user consent mechanisms")
        risks.append("GDPR: Implement data retention and right-to-be-forgotten")
        
        # SOC 2
        risks.append("SOC 2: Implement audit logging")
        risks.append("SOC 2: Define and enforce access controls")
        
        # PCI DSS (if handling payments)
        if any('payment' in f.lower() or 'stripe' in f.lower() for f in important_files):
            risks.append("PCI DSS: Never store raw credit card data")
            risks.append("PCI DSS: Use tokenization for payment processing")
        
        return risks
    
    def _generate_security_recommendations(self, codebase_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive security recommendations."""
        return {
            'immediate_actions': [
                'Audit all configuration files for hardcoded secrets',
                'Review authentication/authorization implementation',
                'Enable HTTPS/TLS for all endpoints',
            ],
            'short_term': [
                'Add input validation to all endpoints',
                'Implement rate limiting',
                'Add comprehensive logging',
                'Set up security headers',
            ],
            'long_term': [
                'Implement WAF (Web Application Firewall)',
                'Set up automated security scanning in CI/CD',
                'Regular security audits and penetration testing',
                'Implement secrets management system',
            ]
        }
    
    def _generate_security_fixes(self, findings: Dict[str, Any]) -> List[str]:
        """Generate ordered security fixes."""
        fixes = []
        
        if findings['critical_vulnerabilities']:
            for vuln in findings['critical_vulnerabilities']:
                fixes.append(f"CRITICAL: {vuln}")
        
        if findings['high_risk_issues']:
            for issue in findings['high_risk_issues'][:3]:
                fixes.append(f"HIGH: {issue}")
        
        recommendations = findings['security_recommendations']
        if recommendations['immediate_actions']:
            fixes.append(f"Immediate: {recommendations['immediate_actions'][0]}")
        
        return fixes
