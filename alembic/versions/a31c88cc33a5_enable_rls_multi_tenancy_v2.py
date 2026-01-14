from alembic import op

revision = "003_enable_rls_multi_tenancy_v2"
down_revision = "504b08949d85"  # initial_schema
branch_labels = None
depends_on = None


def upgrade():
    # ---- SIMPLE tenant_id tables ----
    for table in ["users", "projects", "sdlc_jobs"]:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")

        op.execute(f"""
            DROP POLICY IF EXISTS tenant_isolation_{table} ON {table};
        """)

        op.execute(f"""
            CREATE POLICY tenant_isolation_{table}
            ON {table}
            USING (
                tenant_id = current_setting('app.tenant_id')::uuid
            );
        """)

    # ---- sdlc_job_steps (indirect tenant) ----
    op.execute("ALTER TABLE sdlc_job_steps ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE sdlc_job_steps FORCE ROW LEVEL SECURITY")

    op.execute("""
        DROP POLICY IF EXISTS tenant_isolation_steps ON sdlc_job_steps;
    """)

    op.execute("""
        CREATE POLICY tenant_isolation_steps
        ON sdlc_job_steps
        USING (
            EXISTS (
                SELECT 1
                FROM sdlc_jobs j
                WHERE j.id = sdlc_job_steps.job_id
                  AND j.tenant_id = current_setting('app.tenant_id')::uuid
            )
        );
    """)

    # ---- agent_executions (indirect tenant) ----
    op.execute("ALTER TABLE agent_executions ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE agent_executions FORCE ROW LEVEL SECURITY")

    op.execute("""
        DROP POLICY IF EXISTS tenant_isolation_agent_execs ON agent_executions;
    """)

    op.execute("""
        CREATE POLICY tenant_isolation_agent_execs
        ON agent_executions
        USING (
            EXISTS (
                SELECT 1
                FROM sdlc_job_steps s
                JOIN sdlc_jobs j ON j.id = s.job_id
                WHERE s.id = agent_executions.job_step_id
                  AND j.tenant_id = current_setting('app.tenant_id')::uuid
            )
        );
    """)


def downgrade():
    for table in [
        "agent_executions",
        "sdlc_job_steps",
        "sdlc_jobs",
        "projects",
        "users",
    ]:
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{table} ON {table}")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
