"""
Queue Management System for Social Media Publishing
Implements idempotency, exponential backoff, and rate limiting
"""

import redis
import json
import time
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import random
import hashlib
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.getLogger(__name__)

class JobStatus(Enum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class JobPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class QueueJob:
    """Represents a job in the queue"""
    id: str
    job_type: str
    payload: Dict[str, Any]
    priority: JobPriority = JobPriority.NORMAL
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = None
    scheduled_at: datetime = None
    started_at: datetime = None
    completed_at: datetime = None
    retry_count: int = 0
    max_retries: int = 3
    retry_delay: int = 60  # seconds
    idempotency_key: str = None
    error_message: str = None
    result: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.scheduled_at is None:
            self.scheduled_at = datetime.utcnow()
        if self.idempotency_key is None:
            self.idempotency_key = self._generate_idempotency_key()
    
    def _generate_idempotency_key(self) -> str:
        """Generate idempotency key based on job content"""
        content = f"{self.job_type}:{json.dumps(self.payload, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat() if value else None
            elif isinstance(value, Enum):
                data[key] = value.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueueJob':
        """Create from dictionary"""
        # Convert ISO strings back to datetime objects
        datetime_fields = ['created_at', 'scheduled_at', 'started_at', 'completed_at']
        for field in datetime_fields:
            if data.get(field):
                data[field] = datetime.fromisoformat(data[field])
        
        # Convert enum values
        if 'priority' in data:
            data['priority'] = JobPriority(data['priority'])
        if 'status' in data:
            data['status'] = JobStatus(data['status'])
        
        return cls(**data)

class RateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.limits = {
            'twitter': {'requests': 300, 'window': 900},  # 300 requests per 15 minutes
            'instagram': {'requests': 200, 'window': 3600},  # 200 requests per hour
            'facebook': {'requests': 600, 'window': 3600},  # 600 requests per hour
            'linkedin': {'requests': 100, 'window': 3600},  # 100 requests per hour
        }
    
    def is_allowed(self, platform: str, user_id: str) -> bool:
        """Check if request is allowed under rate limits"""
        if platform not in self.limits:
            return True
        
        limit_config = self.limits[platform]
        key = f"rate_limit:{platform}:{user_id}"
        
        current_count = self.redis.get(key)
        if current_count is None:
            # First request in window
            self.redis.setex(key, limit_config['window'], 1)
            return True
        
        current_count = int(current_count)
        if current_count >= limit_config['requests']:
            return False
        
        # Increment counter
        self.redis.incr(key)
        return True
    
    def get_reset_time(self, platform: str, user_id: str) -> Optional[datetime]:
        """Get when rate limit resets"""
        if platform not in self.limits:
            return None
        
        key = f"rate_limit:{platform}:{user_id}"
        ttl = self.redis.ttl(key)
        
        if ttl > 0:
            return datetime.utcnow() + timedelta(seconds=ttl)
        return None

class QueueManager:
    """Main queue management system"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.rate_limiter = RateLimiter(self.redis)
        self.job_handlers: Dict[str, Callable] = {}
        self.worker_threads: List[threading.Thread] = []
        self.is_running = False
        self.max_workers = 5
        
        # Queue names
        self.pending_queue = "queue:pending"
        self.processing_queue = "queue:processing"
        self.completed_queue = "queue:completed"
        self.failed_queue = "queue:failed"
        self.retry_queue = "queue:retry"
        
        # Job storage
        self.jobs_key = "jobs"
        self.idempotency_key = "idempotency"
    
    def register_handler(self, job_type: str, handler: Callable):
        """Register a job handler"""
        self.job_handlers[job_type] = handler
        logger.info(f"Registered handler for job type: {job_type}")
    
    def enqueue(self, job: QueueJob) -> str:
        """Add job to queue with idempotency check"""
        # Check for existing job with same idempotency key
        existing_job_id = self.redis.hget(self.idempotency_key, job.idempotency_key)
        if existing_job_id:
            logger.info(f"Job with idempotency key {job.idempotency_key} already exists: {existing_job_id}")
            return existing_job_id
        
        # Store job
        job_data = json.dumps(job.to_dict())
        self.redis.hset(self.jobs_key, job.id, job_data)
        
        # Store idempotency mapping
        self.redis.hset(self.idempotency_key, job.idempotency_key, job.id)
        
        # Add to appropriate queue based on schedule
        if job.scheduled_at <= datetime.utcnow():
            # Immediate execution
            priority_score = job.priority.value * 1000 + int(time.time())
            self.redis.zadd(self.pending_queue, {job.id: priority_score})
            logger.info(f"Enqueued job {job.id} for immediate execution")
        else:
            # Scheduled execution
            scheduled_timestamp = job.scheduled_at.timestamp()
            self.redis.zadd("queue:scheduled", {job.id: scheduled_timestamp})
            logger.info(f"Scheduled job {job.id} for {job.scheduled_at}")
        
        return job.id
    
    def get_job(self, job_id: str) -> Optional[QueueJob]:
        """Get job by ID"""
        job_data = self.redis.hget(self.jobs_key, job_id)
        if not job_data:
            return None
        
        return QueueJob.from_dict(json.loads(job_data))
    
    def update_job(self, job: QueueJob):
        """Update job in storage"""
        job_data = json.dumps(job.to_dict())
        self.redis.hset(self.jobs_key, job.id, job_data)
    
    def dequeue(self) -> Optional[QueueJob]:
        """Get next job from queue"""
        # First check for scheduled jobs that are ready
        self._move_scheduled_jobs()
        
        # Get highest priority job
        job_data = self.redis.zpopmax(self.pending_queue)
        if not job_data:
            return None
        
        job_id = job_data[0][0]
        job = self.get_job(job_id)
        
        if job:
            # Move to processing queue
            job.status = JobStatus.PROCESSING
            job.started_at = datetime.utcnow()
            self.update_job(job)
            
            processing_score = int(time.time())
            self.redis.zadd(self.processing_queue, {job_id: processing_score})
        
        return job
    
    def complete_job(self, job_id: str, result: Dict[str, Any] = None):
        """Mark job as completed"""
        job = self.get_job(job_id)
        if not job:
            return
        
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.result = result or {}
        
        self.update_job(job)
        
        # Move from processing to completed
        self.redis.zrem(self.processing_queue, job_id)
        completed_score = int(time.time())
        self.redis.zadd(self.completed_queue, {job_id: completed_score})
        
        logger.info(f"Job {job_id} completed successfully")
    
    def fail_job(self, job_id: str, error_message: str):
        """Mark job as failed and handle retry logic"""
        job = self.get_job(job_id)
        if not job:
            return
        
        job.error_message = error_message
        job.retry_count += 1
        
        # Remove from processing queue
        self.redis.zrem(self.processing_queue, job_id)
        
        if job.retry_count <= job.max_retries:
            # Schedule retry with exponential backoff
            job.status = JobStatus.RETRYING
            retry_delay = self._calculate_retry_delay(job.retry_count, job.retry_delay)
            retry_time = datetime.utcnow() + timedelta(seconds=retry_delay)
            
            self.update_job(job)
            
            # Add to retry queue
            retry_score = retry_time.timestamp()
            self.redis.zadd(self.retry_queue, {job_id: retry_score})
            
            logger.info(f"Job {job_id} scheduled for retry {job.retry_count}/{job.max_retries} in {retry_delay} seconds")
        else:
            # Max retries exceeded
            job.status = JobStatus.FAILED
            job.completed_at = datetime.utcnow()
            
            self.update_job(job)
            
            # Move to failed queue
            failed_score = int(time.time())
            self.redis.zadd(self.failed_queue, {job_id: failed_score})
            
            logger.error(f"Job {job_id} failed permanently after {job.retry_count} retries: {error_message}")
    
    def cancel_job(self, job_id: str):
        """Cancel a job"""
        job = self.get_job(job_id)
        if not job:
            return False
        
        if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            return False
        
        job.status = JobStatus.CANCELLED
        job.completed_at = datetime.utcnow()
        self.update_job(job)
        
        # Remove from all queues
        self.redis.zrem(self.pending_queue, job_id)
        self.redis.zrem(self.processing_queue, job_id)
        self.redis.zrem(self.retry_queue, job_id)
        self.redis.zrem("queue:scheduled", job_id)
        
        logger.info(f"Job {job_id} cancelled")
        return True
    
    def _move_scheduled_jobs(self):
        """Move scheduled jobs to pending queue if ready"""
        current_time = time.time()
        
        # Get jobs ready for execution
        ready_jobs = self.redis.zrangebyscore("queue:scheduled", 0, current_time)
        
        for job_id in ready_jobs:
            job = self.get_job(job_id)
            if job:
                # Move to pending queue
                priority_score = job.priority.value * 1000 + int(time.time())
                self.redis.zadd(self.pending_queue, {job_id: priority_score})
                
                # Remove from scheduled queue
                self.redis.zrem("queue:scheduled", job_id)
                
                logger.info(f"Moved scheduled job {job_id} to pending queue")
        
        # Also check retry queue
        ready_retries = self.redis.zrangebyscore(self.retry_queue, 0, current_time)
        
        for job_id in ready_retries:
            job = self.get_job(job_id)
            if job:
                job.status = JobStatus.PENDING
                self.update_job(job)
                
                # Move to pending queue
                priority_score = job.priority.value * 1000 + int(time.time())
                self.redis.zadd(self.pending_queue, {job_id: priority_score})
                
                # Remove from retry queue
                self.redis.zrem(self.retry_queue, job_id)
                
                logger.info(f"Moved retry job {job_id} to pending queue")
    
    def _calculate_retry_delay(self, retry_count: int, base_delay: int) -> int:
        """Calculate retry delay with exponential backoff and jitter"""
        # Exponential backoff: base_delay * (2 ^ (retry_count - 1))
        delay = base_delay * (2 ** (retry_count - 1))
        
        # Add jitter (±25%)
        jitter = random.uniform(0.75, 1.25)
        delay = int(delay * jitter)
        
        # Cap at 1 hour
        return min(delay, 3600)
    
    def process_job(self, job: QueueJob) -> bool:
        """Process a single job"""
        try:
            # Check rate limits
            platform = job.payload.get('platform')
            user_id = job.payload.get('user_id')
            
            if platform and user_id:
                if not self.rate_limiter.is_allowed(platform, str(user_id)):
                    reset_time = self.rate_limiter.get_reset_time(platform, str(user_id))
                    error_msg = f"Rate limit exceeded for {platform}. Resets at {reset_time}"
                    logger.warning(error_msg)
                    
                    # Reschedule job for after rate limit reset
                    if reset_time:
                        job.scheduled_at = reset_time + timedelta(seconds=60)  # Add buffer
                        job.status = JobStatus.PENDING
                        self.update_job(job)
                        
                        scheduled_score = job.scheduled_at.timestamp()
                        self.redis.zadd("queue:scheduled", {job.id: scheduled_score})
                        
                        return True
                    else:
                        raise Exception(error_msg)
            
            # Get handler for job type
            handler = self.job_handlers.get(job.job_type)
            if not handler:
                raise Exception(f"No handler registered for job type: {job.job_type}")
            
            # Execute job
            logger.info(f"Processing job {job.id} of type {job.job_type}")
            result = handler(job.payload)
            
            # Mark as completed
            self.complete_job(job.id, result)
            return True
            
        except Exception as e:
            logger.error(f"Error processing job {job.id}: {str(e)}")
            self.fail_job(job.id, str(e))
            return False
    
    def start_workers(self, num_workers: int = None):
        """Start worker threads"""
        if self.is_running:
            return
        
        self.is_running = True
        num_workers = num_workers or self.max_workers
        
        for i in range(num_workers):
            worker = threading.Thread(target=self._worker_loop, args=(i,))
            worker.daemon = True
            worker.start()
            self.worker_threads.append(worker)
        
        logger.info(f"Started {num_workers} worker threads")
    
    def stop_workers(self):
        """Stop worker threads"""
        self.is_running = False
        
        # Wait for workers to finish
        for worker in self.worker_threads:
            worker.join(timeout=30)
        
        self.worker_threads.clear()
        logger.info("Stopped all worker threads")
    
    def _worker_loop(self, worker_id: int):
        """Main worker loop"""
        logger.info(f"Worker {worker_id} started")
        
        while self.is_running:
            try:
                job = self.dequeue()
                if job:
                    self.process_job(job)
                else:
                    # No jobs available, sleep briefly
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {str(e)}")
                time.sleep(5)
        
        logger.info(f"Worker {worker_id} stopped")
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        return {
            'pending': self.redis.zcard(self.pending_queue),
            'processing': self.redis.zcard(self.processing_queue),
            'completed': self.redis.zcard(self.completed_queue),
            'failed': self.redis.zcard(self.failed_queue),
            'retry': self.redis.zcard(self.retry_queue),
            'scheduled': self.redis.zcard("queue:scheduled"),
            'total_jobs': self.redis.hlen(self.jobs_key)
        }
    
    def cleanup_old_jobs(self, days: int = 7):
        """Clean up old completed/failed jobs"""
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        # Remove old completed jobs
        old_completed = self.redis.zrangebyscore(self.completed_queue, 0, cutoff_time)
        if old_completed:
            self.redis.zremrangebyscore(self.completed_queue, 0, cutoff_time)
            for job_id in old_completed:
                self.redis.hdel(self.jobs_key, job_id)
        
        # Remove old failed jobs
        old_failed = self.redis.zrangebyscore(self.failed_queue, 0, cutoff_time)
        if old_failed:
            self.redis.zremrangebyscore(self.failed_queue, 0, cutoff_time)
            for job_id in old_failed:
                self.redis.hdel(self.jobs_key, job_id)
        
        logger.info(f"Cleaned up {len(old_completed)} completed and {len(old_failed)} failed jobs older than {days} days")

# Global queue manager instance
queue_manager = QueueManager()

# Job creation helpers
def create_post_job(unified_post_id: int, platform: str, user_id: int, 
                   scheduled_time: datetime = None, priority: JobPriority = JobPriority.NORMAL) -> QueueJob:
    """Create a social media post job"""
    job_id = str(uuid.uuid4())
    
    return QueueJob(
        id=job_id,
        job_type="social_media_post",
        payload={
            "unified_post_id": unified_post_id,
            "platform": platform,
            "user_id": user_id
        },
        priority=priority,
        scheduled_at=scheduled_time or datetime.utcnow()
    )

def create_analytics_job(user_id: int, platform: str, 
                        scheduled_time: datetime = None) -> QueueJob:
    """Create an analytics sync job"""
    job_id = str(uuid.uuid4())
    
    return QueueJob(
        id=job_id,
        job_type="analytics_sync",
        payload={
            "user_id": user_id,
            "platform": platform
        },
        priority=JobPriority.LOW,
        scheduled_at=scheduled_time or datetime.utcnow()
    )

def create_media_upload_job(media_item_id: int, platform: str, user_id: int) -> QueueJob:
    """Create a media upload job"""
    job_id = str(uuid.uuid4())
    
    return QueueJob(
        id=job_id,
        job_type="media_upload",
        payload={
            "media_item_id": media_item_id,
            "platform": platform,
            "user_id": user_id
        },
        priority=JobPriority.HIGH
    )

