import sqlite3
import json
import contextlib
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from tasklite.models import Job, JobStatus
from tasklite.errors import DatabaseError

def to_utc_iso(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    return dt.astimezone(timezone.utc).isoformat()

def from_utc_iso(iso_str: Optional[str]) -> Optional[datetime]:
    if not iso_str:
        return None
    return datetime.fromisoformat(iso_str)

class TaskStore:
    def __init__(self, db_path: str = "tasklite.db"):
        self.db_path = db_path
        self._init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with contextlib.closing(self.get_connection()) as conn:
            with conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS jobs (
                        id TEXT PRIMARY KEY,
                        queue TEXT NOT NULL,
                        handler TEXT NOT NULL,
                        payload TEXT NOT NULL,
                        status TEXT NOT NULL,
                        priority INTEGER NOT NULL,
                        attempts INTEGER NOT NULL,
                        max_retries INTEGER NOT NULL,
                        timeout_seconds INTEGER NOT NULL,
                        error_message TEXT,
                        scheduled_at TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        lease_expires_at TEXT
                    )
                ''')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_jobs_queue_status ON jobs(queue, status)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_jobs_claim ON jobs(queue, status, priority DESC, created_at ASC)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_jobs_scheduled ON jobs(scheduled_at)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_jobs_lease ON jobs(lease_expires_at)')

    def insert_job(self, job: Job) -> str:
        try:
            with contextlib.closing(self.get_connection()) as conn:
                with conn:
                    conn.execute('''
                        INSERT INTO jobs (
                            id, queue, handler, payload, status, priority, attempts, 
                            max_retries, timeout_seconds, error_message, scheduled_at, 
                            created_at, updated_at, lease_expires_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        job.id, job.queue, job.handler, json.dumps(job.payload),
                        job.status.value, job.priority, job.attempts, job.max_retries,
                        job.timeout_seconds, job.error_message,
                        to_utc_iso(job.scheduled_at),
                        to_utc_iso(job.created_at),
                        to_utc_iso(job.updated_at),
                        to_utc_iso(job.lease_expires_at)
                    ))
            return job.id
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to insert job: {e}")

    def _row_to_job(self, row: sqlite3.Row) -> Job:
        return Job(
            id=row['id'],
            queue=row['queue'],
            handler=row['handler'],
            payload=json.loads(row['payload']),
            status=JobStatus(row['status']),
            priority=row['priority'],
            attempts=row['attempts'],
            max_retries=row['max_retries'],
            timeout_seconds=row['timeout_seconds'],
            error_message=row['error_message'],
            scheduled_at=from_utc_iso(row['scheduled_at']),
            created_at=from_utc_iso(row['created_at']),
            updated_at=from_utc_iso(row['updated_at']),
            lease_expires_at=from_utc_iso(row['lease_expires_at'])
        )

    def get_job(self, job_id: str) -> Optional[Job]:
        with contextlib.closing(self.get_connection()) as conn:
            with conn:
                cur = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
                row = cur.fetchone()
                if row:
                    return self._row_to_job(row)
                return None

    def claim_next_job(self, queue: str, worker_id: str, lease_duration_seconds: int = 30) -> Optional[Job]:
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        now_iso = to_utc_iso(now)
        lease_expires = to_utc_iso(now + timedelta(seconds=lease_duration_seconds))
        
        with contextlib.closing(self.get_connection()) as conn:
            with conn:
                conn.execute("BEGIN IMMEDIATE")
                cur = conn.execute('''
                    SELECT * FROM jobs 
                    WHERE queue = ? AND status = 'queued' AND scheduled_at <= ?
                    ORDER BY priority DESC, created_at ASC
                    LIMIT 1
                ''', (queue, now_iso))
                row = cur.fetchone()
                if not row:
                    return None
                
                job_id = row['id']
                attempts = row['attempts'] + 1
                conn.execute('''
                    UPDATE jobs 
                    SET status = 'running', lease_expires_at = ?, attempts = ?, updated_at = ?
                    WHERE id = ?
                ''', (lease_expires, attempts, now_iso, job_id))
                
                cur = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
                updated_row = cur.fetchone()
                return self._row_to_job(updated_row)

    def mark_succeeded(self, job_id: str, result: Optional[Dict[str, Any]] = None):
        now_iso = to_utc_iso(datetime.now(timezone.utc))
        with contextlib.closing(self.get_connection()) as conn:
            with conn:
                conn.execute('''
                    UPDATE jobs
                    SET status = 'succeeded', updated_at = ?, lease_expires_at = NULL
                    WHERE id = ?
                ''', (now_iso, job_id))

    def mark_failed(self, job_id: str, error: str, next_retry_at: Optional[datetime] = None):
        now_iso = to_utc_iso(datetime.now(timezone.utc))
        with contextlib.closing(self.get_connection()) as conn:
            with conn:
                if next_retry_at:
                    conn.execute('''
                        UPDATE jobs
                        SET status = 'queued', scheduled_at = ?, error_message = ?, updated_at = ?, lease_expires_at = NULL
                        WHERE id = ?
                    ''', (to_utc_iso(next_retry_at), error, now_iso, job_id))
                else:
                    conn.execute('''
                        UPDATE jobs
                        SET status = 'failed', error_message = ?, updated_at = ?, lease_expires_at = NULL
                        WHERE id = ?
                    ''', (error, now_iso, job_id))

    def mark_cancelled(self, job_id: str):
        now_iso = to_utc_iso(datetime.now(timezone.utc))
        with contextlib.closing(self.get_connection()) as conn:
            with conn:
                conn.execute('''
                    UPDATE jobs
                    SET status = 'cancelled', updated_at = ?, lease_expires_at = NULL
                    WHERE id = ?
                ''', (now_iso, job_id))

    def reclaim_expired_leases(self) -> int:
        now_iso = to_utc_iso(datetime.now(timezone.utc))
        with contextlib.closing(self.get_connection()) as conn:
            with conn:
                cur = conn.execute('''
                    UPDATE jobs
                    SET status = 'queued', lease_expires_at = NULL, updated_at = ?
                    WHERE status = 'running' AND lease_expires_at < ?
                ''', (now_iso, now_iso))
                return cur.rowcount

    def list_jobs(self, queue: Optional[str] = None, status: Optional[str] = None, limit: int = 100) -> List[Job]:
        with contextlib.closing(self.get_connection()) as conn:
            with conn:
                query = "SELECT * FROM jobs"
                conditions = []
                params = []
                
                if queue:
                    conditions.append("queue = ?")
                    params.append(queue)
                if status:
                    conditions.append("status = ?")
                    params.append(status)
                    
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                    
                query += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)
                
                cur = conn.execute(query, params)
                return [self._row_to_job(row) for row in cur.fetchall()]

    def get_stats(self, queue: Optional[str] = None) -> Dict[str, int]:
        with contextlib.closing(self.get_connection()) as conn:
            with conn:
                query = "SELECT status, count(*) as count FROM jobs"
                params = []
                if queue:
                    query += " WHERE queue = ?"
                    params.append(queue)
                query += " GROUP BY status"
                cur = conn.execute(query, params)
                stats = {status.value: 0 for status in JobStatus}
                total = 0
                for row in cur.fetchall():
                    stats[row['status']] = row['count']
                    total += row['count']
                stats['total'] = total
                return stats
