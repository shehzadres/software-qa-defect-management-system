-- Simulated training execution distribution
SELECT status,COUNT(*) AS total FROM test_executions GROUP BY status;
-- Actual local target run metrics
SELECT COUNT(*) planned,
SUM(status<>'Not Run') executed,
SUM(status='PASS') passed,
SUM(status='FAIL') failed,
ROUND(100.0*SUM(status<>'Not Run')/COUNT(*),2) execution_rate_pct,
ROUND(100.0*SUM(status='PASS')/NULLIF(SUM(status<>'Not Run'),0),2) pass_rate_pct
FROM live_test_executions;
-- Actual cases not executed
SELECT test_case_id,actual_evidence FROM live_test_executions WHERE status='Not Run';
-- Open seeded training defects; do not report these as live findings
SELECT defect_id,summary,severity,priority,status FROM defects
WHERE severity IN ('Critical','High') AND status NOT IN ('Closed','Rejected','Duplicate');
-- Requirement traceability
SELECT r.requirement_id,r.title,COUNT(t.test_case_id) linked_cases
FROM requirements r LEFT JOIN traceability t USING(requirement_id)
GROUP BY r.requirement_id,r.title ORDER BY r.requirement_id;
-- Actual live failures, if any
SELECT test_case_id,actual_evidence FROM live_test_executions WHERE status='FAIL';
-- Defect lifecycle history
SELECT * FROM defect_history ORDER BY defect_id,history_id;
